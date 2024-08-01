export enum Roles {
    'GP_ADMIN' = 555053913108,
    'GP_CLINICAL' = 555053912107,
    'PCSE' = 555053975103,
    'GP_ADMIN_BSOL' = 555056245106,
    'SMOKE_GP_CLINICAL_H85686' = 555054025105, // anything prefixed with smoke shouldnt be used for cy.login
    'SMOKE_GP_ADMIN_H85686' = 555054024104,
}

export const roleIds = Object.values(Roles) as Array<Roles>;
export const roleList = Object.keys(Roles) as Array<string>;
export const roleName = (role: Roles) =>
    roleList.find((roleName) => Roles[roleName] === role) ?? '';
