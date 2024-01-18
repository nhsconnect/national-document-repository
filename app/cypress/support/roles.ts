export enum Roles {
    'GP_ADMIN' = 555053928105,
    'GP_ADMIN_H85686' = 555054037109,
    'GP_CLINICAL' = 555053929106,
    'GP_CLINICAL_H85686' = 555054036108,
    'PCSE' = 555053983103,
}

export const roleIds = Object.values(Roles) as Array<Roles>;
export const roleList = Object.keys(Roles) as Array<string>;
export const roleName = (role: Roles) =>
    roleList.find((roleName) => Roles[roleName] === role) ?? '';
