export type UserAuth = {
    organisations: Array<Organisation>;
    authorisation_token: string;
};

export type Organisation = {
    org_name: string;
    ods_code: string;
    role: Role;
};

export type Role = 'DEV' | 'PCSE' | 'GP';
