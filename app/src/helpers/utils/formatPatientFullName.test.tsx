import { buildPatientDetails } from "../test/testBuilders";
import { getFormattedPatientFullName } from "./formatPatientFullName";

const patientDetails = buildPatientDetails();

describe('getFormattedPatientFullName', () => {
  test.each([
        ['Doe', ['John'], 'Doe, John'],
        ['Doe', ['John,Michael'], 'Doe, John Michael'],
        ['  Doe ', ['  John ,  Michael '], 'Doe, John Michael'],
        ['Doe', [''], 'Doe,'],
        ['', ['John'], ', John'],
        ['', [''], ',']
    ])('should format "%s" and "%s" as "%s"', (familyName, givenName, expected) => {
        patientDetails.familyName = familyName;
        patientDetails.givenName = givenName;
        expect(getFormattedPatientFullName(patientDetails)).toBe(expected);
    });

    it('should handle null input', () => {
        expect(getFormattedPatientFullName(null)).toBe(',');
    });
});
