import { UploadFilesErrors } from '../../types/pages/UploadDocumentsPage/types';

export enum UPLOAD_FILE_ERROR_TYPE {
    noFiles = 'noFiles',
    duplicateFile = 'duplicateFile',
    fileTypeError = 'fileTypeError',
    fileSizeError = 'fileSizeError',
    generalFileNameError = 'generalFileNameError',
    dateOfBirthError = 'dateOfBirthError',
    patientNameError = 'patientNameError',
    nhsNumberError = 'nhsNumberError',
    totalFileNumberUnmatchError = 'totalFileNumberUnmatchError',
    fileNumberMissingError = 'fileNumberMissingError',
    fileNumberOutOfRangeError = 'fileNumberOutOfRangeError',
}

export function getInlineErrorMessage(uploadFileError: UploadFilesErrors): string {
    return fileUploadErrorMessages[uploadFileError.error].inline;
}

export function getErrorBoxErrorMessage(uploadFileError: UploadFilesErrors): string {
    return fileUploadErrorMessages[uploadFileError.error].errorBox;
}

export type fileUploadErrorMessageType = {
    inline: string;
    errorBox: string;
};

type errorMessageType = { [errorType in UPLOAD_FILE_ERROR_TYPE]: fileUploadErrorMessageType };
export const fileUploadErrorMessages: errorMessageType = {
    noFiles: {
        inline: 'You did not select any file to upload',
        errorBox: 'You did not select any file to upload',
    },
    duplicateFile: {
        inline: 'The file has the same name as another',
        errorBox:
            'This file has the same name as another file you selected. Check the name of these file(s) and try again.',
    },
    fileTypeError: {
        inline: 'The file must be in a PDF file format',
        errorBox: 'All files should be in a PDF format',
    },
    fileSizeError: {
        inline: 'Please ensure that all files are less than 5GB in size',
        errorBox: 'Please ensure that all files are less than 5GB in size',
    },
    generalFileNameError: {
        inline: 'Your file has an incorrect filename',
        errorBox:
            'Your filename must follow the format [PDFnumber]_Lloyd_George_Record_[Patient Name]_[NHS Number]_[D.O.B].PDF',
    },
    dateOfBirthError: {
        inline: 'The patient’s date of birth does not match this filename',
        errorBox: 'The patient’s date of birth does not match this filename',
    },
    patientNameError: {
        inline: 'The patient’s name does not match this filename',
        errorBox: 'The patient’s name does not match this filename',
    },
    nhsNumberError: {
        inline: 'The patient’s NHS number does not match this filename',
        errorBox: 'The patient’s NHS number does not match this filename',
    },
    totalFileNumberUnmatchError: {
        inline: 'The total file number does not match with each others',
        errorBox: 'The total file number does not match with each others',
    },
    fileNumberMissingError: {
        inline: 'This record is missing some files with file numbers',
        errorBox: 'This record is missing some files with file numbers',
    },
    fileNumberOutOfRangeError: {
        inline: 'The file number does not match the total number',
        errorBox: 'Some file numbers does not match the total file number',
    },
};
