export enum REPOSITORY_ROLE {
    GP_ADMIN = 'GP_ADMIN',
    GP_CLINICAL = 'GP_CLINICAL',
    PCSE = 'PCSE',
}

export const authorisedRoles: Array<REPOSITORY_ROLE> = Object.values(REPOSITORY_ROLE);
