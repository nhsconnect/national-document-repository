import { dateOfBirthMatches, validateFilenamesWithPatientDetail } from './uploadDocumentValidation';
import { PatientDetails } from '../../types/generic/patientDetails';
import { buildLgFile, buildPatientDetails } from '../test/testBuilders';

describe('validateFilenamesWithPatientDetail', () => {
    const testPatient: PatientDetails = buildPatientDetails({
        familyName: 'Bloggs',
        givenName: ['Jane', 'Smith'],
    });

    // TODO: implement unit test
    it('return an empty array if all filenames are correct', () => {
        expect(1 + 1).toEqual(2);
        // const file1 = buildLgFile(1, 2, 'Joe Doe');
        // const file2 = buildLgFile(2, 2, 'Joe Doe');
        // validateFilenamesWithPatientDetail([file])
    });
});
