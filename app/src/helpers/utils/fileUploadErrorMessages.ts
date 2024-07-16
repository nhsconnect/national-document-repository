export type fileUploadErrorMessageType = {
    message: string;
    errorBox: string;
};

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

type errorMessageType = { [errorType in UPLOAD_FILE_ERROR_TYPE]: fileUploadErrorMessageType };
export const fileUploadErrorMessages: errorMessageType = {
    noFiles: {
        message: 'You did not select any file to upload',
        errorBox: 'You did not select any file to upload',
    },
    duplicateFile: {
        message: 'The file has the same name as another',
        errorBox:
            'This file has the same name as another file you selected. Check the name of these file(s) and try again.',
    },
    fileTypeError: {
        message: 'The file must be in a PDF file format',
        errorBox: 'All files should be in a PDF format',
    },
    fileSizeError: {
        message: 'Please ensure that all files are less than 5GB in size',
        errorBox: 'Please ensure that all files are less than 5GB in size',
    },
    generalFileNameError: {
        message: 'Your file has an incorrect filename',
        errorBox:
            'Your filename must follow the format [PDFnumber]_Lloyd_George_Record_[Patient Name]_[NHS Number]_[D.O.B].PDF',
    },
    dateOfBirthError: {
        message: 'The patient’s date of birth does not match this filename',
        errorBox: 'The patient’s date of birth does not match this filename',
    },
    patientNameError: {
        message: 'The patient’s name does not match this filename',
        errorBox: 'The patient’s name does not match this filename',
    },
    nhsNumberError: {
        message: 'The patient’s NHS number does not match this filename',
        errorBox: 'The patient’s NHS number does not match this filename',
    },
    totalFileNumberUnmatchError: {
        message: 'The total file number does not match with each others',
        errorBox: 'The total file number does not match with each others',
    },
    fileNumberMissingError: {
        message: 'This record is missing some files with file numbers',
        errorBox: 'This record is missing some files with file numbers',
    },
    fileNumberOutOfRangeError: {
        message: 'The file number does not match the total number',
        errorBox: 'Some file numbers does not match the total file number',
    },
};
