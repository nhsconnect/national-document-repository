import { UploadDocument, UploadFilesErrors } from '../../types/pages/UploadDocumentsPage/types';
import { fileUploadErrorMessages } from './fileUploadErrorMessages';
import { PatientDetails } from '../../types/generic/patientDetails';
import moment from 'moment/moment';

let REGEX_ACCENT_MARKS_IN_NFD = '';
for (let i = 0x300; i < 0x371; i++) {
    REGEX_ACCENT_MARKS_IN_NFD += String.fromCharCode(i);
}
const REGEX_ACCENT_CHARS_IN_NFC = 'À-ž';
const REGEX_PATIENT_NAME_PATTERN = `[A-Za-z ${REGEX_ACCENT_CHARS_IN_NFC}${REGEX_ACCENT_MARKS_IN_NFD}'-]+`;
const REGEX_NHS_NUMBER_REGEX = '[0-9]{10}';
const REGEX_LLOYD_GEORGE_FILENAME = new RegExp(
    `^(?<file_number>[0-9])+of(?<total_number>[0-9])+_Lloyd_George_Record_\\[(?<patient_name>${REGEX_PATIENT_NAME_PATTERN})]_\\[(?<nhs_number>${REGEX_NHS_NUMBER_REGEX})]_\\[(?<dob>\\d\\d-\\d\\d-\\d\\d\\d\\d)].pdf$`,
);

export const uploadDocumentValidation = (
    uploadDocuments: UploadDocument[],
    patientDetails: PatientDetails | null,
): UploadFilesErrors[] => {
    const errors: UploadFilesErrors[] = [];

    const FIVEGB = 5 * Math.pow(1024, 3);

    const filesPassedRegexCheck = [];

    for (let document of uploadDocuments) {
        const currentFile = document.file;
        if (currentFile.size > FIVEGB) {
            errors.push({
                filename: currentFile.name,
                error: fileUploadErrorMessages.fileSizeError,
            });
            continue;
        }
        if (currentFile.type !== 'application/pdf') {
            errors.push({
                filename: currentFile.name,
                error: fileUploadErrorMessages.fileTypeError,
            });
            continue;
        }
        const isDuplicate = uploadDocuments.some((compare: UploadDocument) => {
            return currentFile.name === compare.file.name && document.id !== compare.id;
        });
        if (isDuplicate) {
            errors.push({
                filename: document.file.name,
                error: fileUploadErrorMessages.duplicateFile,
            });
            continue;
        }

        const regexMatchResult = REGEX_LLOYD_GEORGE_FILENAME.exec(currentFile.name);
        if (regexMatchResult) {
            filesPassedRegexCheck.push(regexMatchResult);
        } else {
            errors.push({
                filename: currentFile.name,
                error: fileUploadErrorMessages.generalFileNameError,
            });
        }
    }

    if (patientDetails) {
        const errorsWhenCompareWithPdsData = filesPassedRegexCheck.flatMap((regexMatchResult) =>
            validateWithPatientDetails(regexMatchResult, patientDetails),
        );
        errors.push(...errorsWhenCompareWithPdsData);
    }

    const fileNumberErrors = validateFileNumbers(filesPassedRegexCheck);
    errors.push(...fileNumberErrors);

    return errors;
};

const fromOneToN = (size: number): number[] => {
    const result = [];
    for (let i = 1; i <= size; i++) {
        result.push(i);
    }
    return result;
};

const validateFileNumbers = (regexMatchResults: RegExpExecArray[]): UploadFilesErrors[] => {
    const errors: UploadFilesErrors[] = [];
    const allFileNames = regexMatchResults.map((match) => match.input);

    const totalNumberInFiles = new Set(
        regexMatchResults.map((match) => match?.groups?.total_number),
    );
    if (totalNumberInFiles.size !== 1) {
        // early return here.
        const totalNumberUnmatchErrors = allFileNames.map((filename) => ({
            filename,
            error: fileUploadErrorMessages.totalFileNumberUnmatchError,
        }));
        return totalNumberUnmatchErrors;
    }

    const totalFileNumber = Number([...totalNumberInFiles][0]);

    const expectedFileNumbers = new Set(fromOneToN(totalFileNumber));
    const actualFileNumbersFound = regexMatchResults.map((match) => Number(match[1]));
    const actualFileNumbersSet = new Set(actualFileNumbersFound);

    regexMatchResults.forEach((match, index) => {
        const filename = match.input;
        const fileNumber = Number(match?.groups?.file_number);

        if (!expectedFileNumbers.has(fileNumber)) {
            errors.push({ filename, error: fileUploadErrorMessages.fileNumberOutOfRangeError });
        }
        if (actualFileNumbersFound.indexOf(fileNumber) !== index) {
            errors.push({ filename, error: fileUploadErrorMessages.duplicateFile });
        }
    });

    const missingFileNumbers = [...expectedFileNumbers].filter(
        (number) => !actualFileNumbersSet.has(number),
    );

    if (missingFileNumbers.length > 0) {
        const missingFileNumbersInString = missingFileNumbers.join(', ');
        const updatedInlineMessage = `${fileUploadErrorMessages.fileNumberMissingError.message}: ${missingFileNumbersInString}`;
        const updatedErrorBoxMessage = `${fileUploadErrorMessages.fileNumberMissingError.errorBox}: ${missingFileNumbersInString}`;

        const missingFileNumberErrors: UploadFilesErrors[] = allFileNames.map((filename) => ({
            filename,
            error: {
                message: updatedInlineMessage,
                errorBox: updatedErrorBoxMessage,
            },
        }));
        errors.push(...missingFileNumberErrors);
    }

    return errors;
};

const validateWithPatientDetails = (
    regexMatchResult: RegExpExecArray,
    patientDetails: PatientDetails,
): UploadFilesErrors[] => {
    const dateOfBirth = new Date(patientDetails.birthDate);
    const dateOfBirthString = moment(dateOfBirth).format('DD-MM-YYYY');
    const nhsNumber = patientDetails.nhsNumber;

    const errors: UploadFilesErrors[] = [];
    const filename = regexMatchResult.input;

    if (regexMatchResult?.groups?.nhs_number !== nhsNumber) {
        errors.push({ filename, error: fileUploadErrorMessages.nhsNumberError });
    }

    if (regexMatchResult?.groups?.dob !== dateOfBirthString) {
        errors.push({ filename, error: fileUploadErrorMessages.dateOfBirthError });
    }

    const patientNameInFilename = regexMatchResult?.groups?.patient_name as string;
    if (!patientNameMatchesPds(patientNameInFilename, patientDetails)) {
        errors.push({ filename, error: fileUploadErrorMessages.patientNameError });
    }

    return errors;
};

export const patientNameMatchesPds = (
    patientNameInFileName: string,
    patientDetailsFromPds: PatientDetails,
): boolean => {
    const patientNameInFileNameNormalised = patientNameInFileName.normalize('NFD').toLowerCase();

    const firstName = patientDetailsFromPds.givenName[0].normalize('NFD').toLowerCase();
    const firstNameMatches = patientNameInFileNameNormalised.startsWith(firstName);

    const familyName = patientDetailsFromPds.familyName.normalize('NFD').toLowerCase();
    const familyNameMarches = patientNameInFileNameNormalised.endsWith(familyName);

    return firstNameMatches && familyNameMarches;
};
