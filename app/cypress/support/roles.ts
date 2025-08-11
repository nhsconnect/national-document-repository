export enum Roles {
    'GP_ADMIN',
    'GP_CLINICAL',
    'PCSE',
    'GP_ADMIN_BSOL',
    'SMOKE_GP_ADMIN' = 'gp_admin',
    'SMOKE_GP_CLINICAL' = 'gp_clinical',
    'SMOKE_PCSE' = 'pcse',
}

const isEnumKey = (k: string): k is keyof typeof Roles => Number.isNaN(Number(k));
const isStringMember = (v: unknown): v is Roles => typeof v === 'string';
export const roleList = Object.keys(Roles).filter(isEnumKey) as Array<keyof typeof Roles>;
export const roleIds = roleList
  .map((k) => Roles[k])
  .filter(isStringMember) as Roles[];
export const roleName = (role: Roles): keyof typeof Roles | '' =>
  roleList.find((k) => isStringMember(Roles[k]) && Roles[k] === role) ?? '';