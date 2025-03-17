export type AccessAuditData = {
    Reasons: string[];
    OtherReasonText?: string;
};

export enum AccessAuditType {
    deceasedPatient = 0,
}

export type PatientAccessAudit = {
    accessAuditType: AccessAuditType;
    accessAuditData: AccessAuditData;
    nhsNumber: string;
};

export enum DeceasedAccessAuditReasons {
    medicalRequest = '01',
    legalRequest = '02',
    familyRequest = '03',
    internalNhsRequest = '04',
    removeRecord = '05',
    anotherReason = '99',
}
