import { patientNameMatchesPds, uploadDocumentValidation } from './uploadDocumentValidation';
import { buildPatientDetails } from '../test/testBuilders';
import {
    buildLGUploadDocsFromFilenames,
    loadTestCases,
    TEST_CASES_FOR_FAMILY_NAME_WITH_HYPHEN,
    TEST_CASES_FOR_TWO_WORDS_FAMILY_NAME,
    TEST_CASES_FOR_TWO_WORDS_FAMILY_NAME_AND_GIVEN_NAME,
    TEST_CASES_FOR_TWO_WORDS_GIVEN_NAME,
} from '../test/testDataForPdsNameValidation';
import { UploadFilesErrors } from '../../types/pages/UploadDocumentsPage/types';

describe('uploadDocumentValidation', () => {
    describe('name validation', () => {
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
