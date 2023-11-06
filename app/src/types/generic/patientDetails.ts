export type PatientDetails = {
    birthDate: string;
    familyName: string;
    givenName: Array<string>;
    nhsNumber: string;
    postalCode: string | null;
    superseded: boolean;
    restricted: boolean;
    active: boolean;
};
