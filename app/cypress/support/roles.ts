export enum Roles {
    'GP_ADMIN',
    'GP_CLINICAL',
    'PCSE',
    'GP_ADMIN_BSOL',
    'SMOKE_GP_ADMIN' = 'gp_admin',
    'SMOKE_GP_CLINICAL' = 'gp_clinical',
    'SMOKE_PCSE' = 'pcse',
}

// possible refactor from enum to exported consts - if we can't keep using the enum with 0 value when necess
export const roleIds = Object.values(Roles) as Array<Roles>;
export const roleList = Object.keys(Roles) as Array<string>;
export const roleName = (role: Roles) =>
    roleList.find((roleName) => Roles[roleName] === role) ?? '';
