import { GenericError } from "../../types/pages/UploadDocumentsPage/types";

type UploadFilesError = GenericError<UPLOAD_FILE_ERROR_TYPE>;

export enum UPLOAD_FILE_ERROR_TYPE {
    noFiles = 'noFiles',
    passwordProtected = 'passwordProtected',
    invalidPdf = 'invalidPdf',
    emptyPdf = 'emptyPdf',
    duplicatePositionError = 'duplicatePositionError',
}

export enum PDF_PARSING_ERROR_TYPE {
    INVALID_PDF_STRUCTURE = 'Invalid PDF structure.',
    PASSWORD_MISSING = 'No password given',
    EMPTY_PDF = 'The PDF file is empty, i.e. its size is zero bytes.',
}

export function getInlineErrorMessage(uploadFileError: UploadFilesError): string {
    const errorMessage = fileUploadErrorMessages[uploadFileError.error].inline;
    if (uploadFileError.details) {
        return `${errorMessage} ${uploadFileError.details}`;
    }
    return errorMessage;
}

export function getErrorBoxErrorMessage(uploadFileError: UploadFilesError): string {
    return fileUploadErrorMessages[uploadFileError.error].errorBox;
}

type UploadFilesErrorBoxMessages = Partial<
    Record<UPLOAD_FILE_ERROR_TYPE, { linkIds: string[]; errorMessage: string }>
>;
export function groupUploadErrorsByType(
    uploadFileErrors: UploadFilesError[],
): UploadFilesErrorBoxMessages {
    const result: UploadFilesErrorBoxMessages = {};

    uploadFileErrors.forEach((errorItem) => {
        const { error, linkId = '' } = errorItem;
        const errorMessage = getErrorBoxErrorMessage(errorItem);
        if (!(error in result)) {
            result[error] = { linkIds: [linkId], errorMessage };
        } else {
            result[error]?.linkIds?.push(linkId);
        }
    });

    return result;
}

export type fileUploadErrorMessageType = {
    inline: string;
    errorBox: string;
};

type errorMessageType = { [errorType in UPLOAD_FILE_ERROR_TYPE]: fileUploadErrorMessageType };
export const fileUploadErrorMessages: errorMessageType = {
    noFiles: {
        inline: 'Select a file to upload',
        errorBox: 'Select a file to upload',
    },
    invalidPdf: {
        inline: 'The selected file is be damaged or unreadable. Fix it to continue with upload.',
        errorBox: 'The selected file is be damaged or unreadable. Fix it to continue with upload.',
    },
    passwordProtected: {
        inline: 'The selected file is password protected. Remove password and upload again.',
        errorBox: 'The selected file is password protected. Remove password and upload again.',
    },
    emptyPdf: {
        inline: 'The selected file is empty. Check it to continue with upload.',
        errorBox: 'The selected file is empty. Check it to continue with upload.',
    },
    duplicatePositionError: {
        inline: 'You have selected the same position number for two or more files',
        errorBox: 'You have selected the same position number for two or more files',
    }
};
