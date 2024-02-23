// TODO: put in seperate helper function, input UploadDoc[] output fileErrors[]
import { UploadDocument, UploadFilesErrors } from '../../types/pages/UploadDocumentsPage/types';

export const uploadDocumentValidation = (uploadDocuments: UploadDocument[]) => {
    let REGEX_ACCENT_MARKS_IN_NFD = '';
    for (let i = 300; i < 371; i++) {
        REGEX_ACCENT_MARKS_IN_NFD += String.fromCharCode(i);
    }
    const REGEX_ACCENT_CHARS_IN_NFC = 'À-ž';
    const REGEX_PATIENT_NAME_PATTERN = `[A-Za-z ${REGEX_ACCENT_CHARS_IN_NFC}${REGEX_ACCENT_MARKS_IN_NFD}]+`;
    const REGEX_NHS_NUMBER_REGEX = '[0-9]{10}';
    const REGEX_LLOYD_GEORGE_FILENAME = new RegExp(
        `[0-9]+of[0-9]+_Lloyd_George_Record_\\[${REGEX_PATIENT_NAME_PATTERN}]_\\[${REGEX_NHS_NUMBER_REGEX}]_\\[\\d\\d-\\d\\d-\\d\\d\\d\\d].pdf`,
    );
    const errors: UploadFilesErrors[] = [];
    const lgFilesNumber = /of[0-9]+/;
    const FIVEGB = 5 * Math.pow(1024, 3);
    for (let i = 0; i < uploadDocuments.length; i++) {
        const currentFile = uploadDocuments[i].file;
        if (currentFile.size > FIVEGB) {
            errors.push({
                file: uploadDocuments[i],
                error: 'Please ensure that all files are less than 5GB in size',
            });
            continue;
        }
        if (currentFile.type !== 'application/pdf') {
            errors.push({
                file: uploadDocuments[i],
                error: 'One or more of the files do not match the required file type. Please check the file(s) and try again',
            });
            continue;
        }
        const isDuplicate = uploadDocuments?.some((compare: UploadDocument) => {
            return (
                uploadDocuments[i].file.name === compare.file.name &&
                uploadDocuments[i].file.size === compare.file.size &&
                uploadDocuments[i].id !== compare.id
            );
        });
        if (isDuplicate) {
            errors.push({
                file: uploadDocuments[i],
                error: 'There are documents chosen that have the same name, a record with duplicate file names can not be uploaded because it does not match the required file format. Please check the files(s) and try again.',
            });
            continue;
        }

        const expectedNumberOfFiles = currentFile.name.match(lgFilesNumber);
        const doesPassRegex = REGEX_LLOYD_GEORGE_FILENAME.exec(currentFile.name);
        const doFilesTotalMatch =
            expectedNumberOfFiles &&
            uploadDocuments.length === parseInt(expectedNumberOfFiles[0].slice(2));
        const isFileNumberBiggerThanTotal =
            expectedNumberOfFiles &&
            parseInt(currentFile.name.split(lgFilesNumber)[0]) >
                parseInt(expectedNumberOfFiles[0].slice(2));
        const isFileNumberZero = currentFile.name.split(lgFilesNumber)[0] === '0';
        const doesFileNameMatchEachOther =
            currentFile.name.split(lgFilesNumber)[1] ===
            uploadDocuments[0].file.name.split(lgFilesNumber)[1];
        if (
            !doesPassRegex ||
            !doFilesTotalMatch ||
            isFileNumberBiggerThanTotal ||
            isFileNumberZero ||
            !doesFileNameMatchEachOther
        ) {
            errors.push({
                file: uploadDocuments[i],
                error: 'One or more of the files do not match the required filename format. Please check the file(s) and try again',
            });
        }
    }
    return errors;
};
