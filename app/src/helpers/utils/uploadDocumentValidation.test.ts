import { patientNameMatchesPds, uploadDocumentValidation } from './uploadDocumentValidation';
import {
    buildDocument,
    buildLgFile,
    buildPatientDetails,
    buildTextFile,
} from '../test/testBuilders';
import {
    buildLGUploadDocsFromFilenames,
    loadTestCases,
    TEST_CASES_FOR_FAMILY_NAME_WITH_HYPHEN,
    TEST_CASES_FOR_TWO_WORDS_FAMILY_NAME,
    TEST_CASES_FOR_TWO_WORDS_FAMILY_NAME_AND_GIVEN_NAME,
    TEST_CASES_FOR_TWO_WORDS_GIVEN_NAME,
} from '../test/testDataForPdsNameValidation';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadFilesErrors,
} from '../../types/pages/UploadDocumentsPage/types';
import { fileUploadErrorMessages, UPLOAD_FILE_ERROR_TYPE } from './fileUploadErrorMessages';

describe('uploadDocumentValidation', () => {
    describe('file validation', () => {
        const testPatient = buildPatientDetails({
            givenName: ['Joe'], // NFC
            familyName: 'Blogs',
            nhsNumber: '9000000009',
            birthDate: '1970-01-01',
        });

        it('detect files larger than 5 GB', () => {
            const largeFile = buildLgFile(1, 2, 'Joe Blogs', 6 * Math.pow(1024, 3));
            const normalFile = buildLgFile(2, 2, 'Joe Blogs');
            const testUploadDocuments = [largeFile, normalFile].map((file) =>
                buildDocument(file, DOCUMENT_UPLOAD_STATE.SELECTED, DOCUMENT_TYPE.LLOYD_GEORGE),
            );

            const expectedError: UploadFilesErrors = {
                filename: largeFile.name,
                error: UPLOAD_FILE_ERROR_TYPE.fileSizeError,
            };
            const actual = uploadDocumentValidation(testUploadDocuments, testPatient);

            expect(actual).toContainEqual(expectedError);
        });

        it('detect file that is not PDF type', () => {
            const nonPdfFile = buildTextFile(
                '1of2_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf',
            );
            const normalFile = buildLgFile(2, 2, 'Joe Blogs');
            const testUploadDocuments = [nonPdfFile, normalFile].map((file) =>
                buildDocument(file, DOCUMENT_UPLOAD_STATE.SELECTED, DOCUMENT_TYPE.LLOYD_GEORGE),
            );

            const expectedError: UploadFilesErrors = {
                filename: nonPdfFile.name,
                error: UPLOAD_FILE_ERROR_TYPE.fileTypeError,
            };
            const actual = uploadDocumentValidation(testUploadDocuments, testPatient);

            expect(actual).toContainEqual(expectedError);
        });

        describe('file names validation', () => {
            it('detect file names duplication', () => {
                const file1 = buildLgFile(1, 2, 'Joe Blogs');
                const anotherFile1 = buildLgFile(1, 2, 'Joe Blogs');
                const file2 = buildLgFile(2, 2, 'Joe Blogs');
                const testUploadDocuments = [file1, anotherFile1, file2].map((file) =>
                    buildDocument(file, DOCUMENT_UPLOAD_STATE.SELECTED, DOCUMENT_TYPE.LLOYD_GEORGE),
                );

                const expectedError: UploadFilesErrors = {
                    filename: file1.name,
                    error: UPLOAD_FILE_ERROR_TYPE.duplicateFile,
                };
                const actual = uploadDocumentValidation(testUploadDocuments, testPatient);

                expect(actual).toContainEqual(expectedError);
            });

            it('detect file name that does not match LG naming convention', () => {
                const invalidFileName = 'some_non_standard_file_name.pdf';
                const testUploadDocuments = buildLGUploadDocsFromFilenames([
                    invalidFileName,
                    '2of2_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf',
                ]);

                const expectedError: UploadFilesErrors = {
                    filename: invalidFileName,
                    error: UPLOAD_FILE_ERROR_TYPE.generalFileNameError,
                };
                const actual = uploadDocumentValidation(testUploadDocuments, testPatient);

                expect(actual).toContainEqual(expectedError);
            });

            it('detect missing file', () => {
                const testFilenames = [
                    '1of5_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf',
                    '3of5_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf',
                    '5of5_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf',
                ];
                const testUploadDocuments = buildLGUploadDocsFromFilenames(testFilenames);

                const expectedErrors = testFilenames.map((filename) => ({
                    filename,
                    error: UPLOAD_FILE_ERROR_TYPE.fileNumberMissingError,
                }));
                const actual = uploadDocumentValidation(testUploadDocuments, testPatient);

                expect(actual).toEqual(expect.arrayContaining(expectedErrors));
            });

            it('detect file number exceeding total number', () => {
                const invalidFileName =
                    '3of2_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf';
                const testFilenames = [
                    '1of2_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf',
                    '2of2_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf',
                    invalidFileName,
                ];
                const testUploadDocuments = buildLGUploadDocsFromFilenames(testFilenames);

                const expectedError = {
                    filename: invalidFileName,
                    error: UPLOAD_FILE_ERROR_TYPE.fileNumberOutOfRangeError,
                };
                const actual = uploadDocumentValidation(testUploadDocuments, testPatient);

                expect(actual).toContainEqual(expectedError);
            });

            it('detect file number duplication', () => {
                const duplicatedFileName =
                    '01of2_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf';
                const testFilenames = [
                    '1of2_Lloyd_George_Record_[Joe Blogs]_[9000000009]_[01-01-1970].pdf',
                    duplicatedFileName,
                ];
                const testUploadDocuments = buildLGUploadDocsFromFilenames(testFilenames);

                const expectedError = {
                    filename: duplicatedFileName,
                    error: UPLOAD_FILE_ERROR_TYPE.duplicateFile,
                };
                const actual = uploadDocumentValidation(testUploadDocuments, testPatient);

                expect(actual).toContainEqual(expectedError);
            });
        });
    });

    describe('patient name validation', () => {
        it('can handle a patient name with multiple words and special chars', () => {
            const testPatient = buildPatientDetails({
                givenName: ['Jane François', 'Bob'], // NFC
                familyName: "O'Brian-Jones Anderson",
                nhsNumber: '9000000009',
                birthDate: '2011-09-19',
            });
            const patientNameInFile = "Jane François Bob O'Brian-Jones Anderson"; // NFD;
            const testFileName = `1of1_Lloyd_George_Record_[${patientNameInFile}]_[9000000009]_[19-09-2011].pdf`;
            const testUploadDocuments = buildLGUploadDocsFromFilenames([testFileName]);

            const expected: UploadFilesErrors[] = [];
            const actual = uploadDocumentValidation(testUploadDocuments, testPatient);

            expect(actual).toEqual(expected);
        });
    });
});

describe('patientNameMatchesPds', () => {
    it('returns true when the name in pds match patientNameInFileName', () => {
        const patientDetails = buildPatientDetails({ givenName: ['Jane'], familyName: 'Smith' });
        const patientNameInFileName = 'Jane Smith';
        const expected: boolean = true;

        const actual: boolean = patientNameMatchesPds(patientNameInFileName, patientDetails);
        expect(actual).toBe(expected);
    });

    it('returns false when first name not match', () => {
        const patientDetails = buildPatientDetails({ givenName: ['Jane'], familyName: 'Smith' });
        const patientNameInFileName = 'Bob Smith';
        const expected: boolean = false;

        const actual: boolean = patientNameMatchesPds(patientNameInFileName, patientDetails);
        expect(actual).toBe(expected);
    });

    it('returns false when last name not match', () => {
        const patientDetails = buildPatientDetails({ givenName: ['Jane'], familyName: 'Smith' });
        const patientNameInFileName = 'Jane Anderson';
        const expected: boolean = false;

        const actual: boolean = patientNameMatchesPds(patientNameInFileName, patientDetails);
        expect(actual).toBe(expected);
    });

    it('should be case insensitive when comparing names', () => {
        const patientDetails = buildPatientDetails({ givenName: ['jane'], familyName: 'SMITH' });
        const patientNameInFileName = 'Jane Smith';
        const expected: boolean = true;

        const actual: boolean = patientNameMatchesPds(patientNameInFileName, patientDetails);
        expect(actual).toBe(expected);
    });

    it('should be able to compare names with accent chars', () => {
        const patientDetails = buildPatientDetails(
            { givenName: ['Jàne'], familyName: 'Smïth' }, // NFD
        );
        const patientNameInFileName = 'Jàne Smïth'; // NFC
        const expected: boolean = true;

        const actual: boolean = patientNameMatchesPds(patientNameInFileName, patientDetails);
        expect(actual).toBe(expected);
    });

    describe('Names with multiple words joined together', () => {
        it.each(loadTestCases(TEST_CASES_FOR_TWO_WORDS_FAMILY_NAME))(
            'from pds: ["Jane", "Bob"] Smith Anderson, filename: $patientNameInFileName, $shouldAcceptName',
            ({ patientDetails, patientNameInFileName, shouldAcceptName }) => {
                const actual: boolean = patientNameMatchesPds(
                    patientNameInFileName,
                    patientDetails,
                );
                const expected: boolean = shouldAcceptName;

                expect(actual).toBe(expected);
            },
        );

        it.each(loadTestCases(TEST_CASES_FOR_FAMILY_NAME_WITH_HYPHEN))(
            'from pds: ["Jane"] Smith-Anderson, filename: $patientNameInFileName, $shouldAcceptName',
            ({ patientDetails, patientNameInFileName, shouldAcceptName }) => {
                const actual: boolean = patientNameMatchesPds(
                    patientNameInFileName,
                    patientDetails,
                );
                const expected: boolean = shouldAcceptName;

                expect(actual).toBe(expected);
            },
        );

        it.each(loadTestCases(TEST_CASES_FOR_TWO_WORDS_GIVEN_NAME))(
            'from pds: ["Jane Bob"] Smith, filename: $patientNameInFileName, $shouldAcceptName',
            ({ patientDetails, patientNameInFileName, shouldAcceptName }) => {
                const actual: boolean = patientNameMatchesPds(
                    patientNameInFileName,
                    patientDetails,
                );
                const expected: boolean = shouldAcceptName;

                expect(actual).toBe(expected);
            },
        );

        it.each(loadTestCases(TEST_CASES_FOR_TWO_WORDS_FAMILY_NAME_AND_GIVEN_NAME))(
            'from pds: ["Jane Bob"] Smith Anderson, filename: $patientNameInFileName, $shouldAcceptName',
            ({ patientDetails, patientNameInFileName, shouldAcceptName }) => {
                const actual: boolean = patientNameMatchesPds(
                    patientNameInFileName,
                    patientDetails,
                );
                const expected: boolean = shouldAcceptName;

                expect(actual).toBe(expected);
            },
        );
    });
});
