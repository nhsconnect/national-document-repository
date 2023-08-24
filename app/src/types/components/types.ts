export type PatientDetails = {
    nhsNumber: number;
    familyName: string;
    givenName: Array<string>;
    birthDate: Date;
    postalCode: string;
};