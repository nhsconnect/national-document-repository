export type Patient = {
  birthDate: string;
  familyName: string;
  givenName: Array<string>;
  nhsNumber: string;
  postalCode: string;
  superseded: boolean;
  restricted: boolean;
};
