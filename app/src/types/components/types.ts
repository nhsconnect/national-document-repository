export type PatientDetails = {
    nhsNumber: string;
    familyName: string;
    givenName: Array<string>;
    birthDate: string;
    postalCode: string;
    superseded: boolean;
    restricted: boolean;
};