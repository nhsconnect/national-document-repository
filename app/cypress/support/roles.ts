// existing:
export const Roles = {
  GP_ADMIN: 'gp_admin',
  GP_CLINICAL: 'gp_clinical',
  PCSE: 'pcse',
  GP_ADMIN_BSOL: 'gp_admin_bsol',
  SMOKE_GP_ADMIN: 'gp_admin',
  SMOKE_GP_CLINICAL: 'gp_clinical',
  SMOKE_PCSE: 'pcse',
} as const;

export type RoleKey = keyof typeof Roles;
export type RoleId  = typeof Roles[RoleKey];

export type RoleInfo = {
    roleId: RoleId;
    roleName: RoleKey;
};

export function roleName(input: RoleKey | RoleId | string): RoleKey {
  const key = String(input).toUpperCase().trim();
  if ((Roles as any)[key]) return key as RoleKey;

  switch (String(input).toLowerCase().trim()) {
    case 'gp_admin_bsol': return 'GP_ADMIN_BSOL';
    case 'gp_admin':      return 'GP_ADMIN';
    case 'gp_clinical':   return 'GP_CLINICAL';
    case 'pcse':          return 'PCSE';
    case 'smoke_gp_admin':    return 'GP_ADMIN';
    case 'smoke_gp_clinical': return 'GP_CLINICAL';
    case 'smoke_pcse':        return 'PCSE';
    default:
      throw new Error(
        `Unknown role '${input}'. Expected one of keys ${Object.keys(Roles).join(', ')} or ids gp_admin|gp_clinical|pcse|gp_admin_bsol`
      );
  }
}

export function roleId(input: RoleKey | RoleId | string): RoleId {
  const key = roleName(input);
  return Roles[key];
}
