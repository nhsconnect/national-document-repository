import { PatientDetails } from "../../types/generic/patientDetails";

export const getFormattedPatientFullName = (patientDetails: PatientDetails | null): string => {
    const familyName = patientDetails?.familyName?.trim() || '';

    const givenNames = patientDetails?.givenName
        ?.flatMap(name => name.split(','))
        .map(name => name.trim())
        .join(' ') || '';

    return `${familyName}, ${givenNames}`.trim();
};
