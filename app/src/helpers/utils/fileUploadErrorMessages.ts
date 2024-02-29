export const fileUploadErrorMessages = {
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
    fileNameError: {
        message: 'Your file has an incorrect filename',
        errorBox:
            'Your filename must follow the format [PDFnumber]_Lloyd_George_Record_[Patient Name]_[NHS Number]_[D.O.B].PDF',
    },
};
