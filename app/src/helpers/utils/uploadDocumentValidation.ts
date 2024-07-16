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
    `^[0-9]+of[0-9]+_Lloyd_George_Record_\\[(?<patient_name>${REGEX_PATIENT_NAME_PATTERN})]_\\[(?<nhs_number>${REGEX_NHS_NUMBER_REGEX})]_\\[(?<dob>\\d\\d-\\d\\d-\\d\\d\\d\\d)].pdf$`,
);

export const uploadDocumentValidation = (
    uploadDocuments: UploadDocument[],
    patientDetails: PatientDetails | null,
): UploadFilesErrors[] => {
    const errors: UploadFilesErrors[] = [];

    const FIVEGB = 5 * Math.pow(1024, 3);
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

        const failedRegexCheck: boolean = !REGEX_LLOYD_GEORGE_FILENAME.exec(currentFile.name);

        if (failedRegexCheck) {
            errors.push({
                filename: currentFile.name,
                error: fileUploadErrorMessages.generalFileNameError,
            });
            continue;
        }

        if (patientDetails) {
            const errorsWhenCompareWithPdsData = validateWithPatientDetails(
                currentFile.name,
                patientDetails,
            );
            errors.push(...errorsWhenCompareWithPdsData);
        }
    }

    const fileNumberErrors = validateFileNumbers(uploadDocuments.map((doc) => doc.file.name));

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

const validateFileNumbers = (filenames: string[]): UploadFilesErrors[] => {
    const errors: UploadFilesErrors[] = [];
    const lgFilesNumber = /^([0-9]+)of([0-9]+)/;

    const allFileNumbersMatches = filenames
        .map((filename) => lgFilesNumber.exec(filename))
        .filter((matchFound) => matchFound) as RegExpExecArray[];

    const allFileNamesWithNumbers = allFileNumbersMatches.map((match) => match.input);

    const allTotalNumbersFound = new Set(allFileNumbersMatches.map((match) => match[2]));
    if (allTotalNumbersFound.size !== 1) {
        // early return here.
        const totalNumberUnmatchErrors = allFileNamesWithNumbers.map((filename) => ({
            filename,
            error: fileUploadErrorMessages.totalFileNumberUnmatchError,
        }));
        return totalNumberUnmatchErrors;
    }

    const totalFileNumber = Number([...allTotalNumbersFound][0]);

    const expectedFileNumbers = new Set(fromOneToN(totalFileNumber));
    const actualFileNumbersFound = allFileNumbersMatches.map((match) => Number(match[1]));
    const actualFileNumbersSet = new Set(actualFileNumbersFound);

    allFileNumbersMatches.forEach((matchData, index) => {
        const filename = matchData.input;
        const fileNumber = Number(matchData[1]);

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

        const missingFileNumberErrors: UploadFilesErrors[] = allFileNamesWithNumbers.map(
            (filename) => ({
                filename,
                error: {
                    message: updatedInlineMessage,
                    errorBox: updatedErrorBoxMessage,
                },
            }),
        );
        errors.push(...missingFileNumberErrors);
    }

    return errors;
};

const fileNumberIsValid = (filename: string, uploadDocuments: UploadDocument[]): boolean => {
    const lgFilesNumber = /of[0-9]+/;
    const expectedNumberOfFiles = lgFilesNumber.exec(filename);
    const doFilesTotalMatch =
        expectedNumberOfFiles !== null &&
        uploadDocuments.length === parseInt(expectedNumberOfFiles[0].slice(2));
    const isFileNumberBiggerThanTotal =
        expectedNumberOfFiles != null &&
        parseInt(filename.split(lgFilesNumber)[0]) > parseInt(expectedNumberOfFiles[0].slice(2));
    const isFileNumberZero = parseInt(filename.split(lgFilesNumber)[0]) === 0;
    const doesFileNameMatchEachOther =
        filename.split(lgFilesNumber)[1] === uploadDocuments[0].file.name.split(lgFilesNumber)[1];
    return (
        doFilesTotalMatch &&
        !isFileNumberBiggerThanTotal &&
        !isFileNumberZero &&
        doesFileNameMatchEachOther
    );
};

const validateWithPatientDetails = (
    filename: string,
    patientDetails: PatientDetails,
): UploadFilesErrors[] => {
    const dateOfBirth = new Date(patientDetails.birthDate);
    const dateOfBirthString = moment(dateOfBirth).format('DD-MM-YYYY');
    const nhsNumber = patientDetails.nhsNumber;

    const errors: UploadFilesErrors[] = [];

    const match = REGEX_LLOYD_GEORGE_FILENAME.exec(filename);

    if (match?.groups?.nhs_number !== nhsNumber) {
        errors.push({ filename, error: fileUploadErrorMessages.nhsNumberError });
    }

    if (match?.groups?.dob !== dateOfBirthString) {
        errors.push({ filename, error: fileUploadErrorMessages.dateOfBirthError });
    }

    const patientNameInFilename = match?.groups?.patient_name as string;
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
