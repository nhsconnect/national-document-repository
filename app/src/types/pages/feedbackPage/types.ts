export type FormData = Record<FORM_FIELDS, string>;

export enum FORM_FIELDS {
    feedbackContent = 'feedbackContent',
    howSatisfied = 'howSatisfied',
    respondentName = 'respondentName',
    respondentEmail = 'respondentEmail',
}

export enum SUBMISSION_STAGE {
    NotSubmitted,
    Submitting,
    Successful,
    Failure,
}

export const SATISFACTION_CHOICES = {
    VerySatisfied: 'Very satisfied',
    Satisfied: 'Satisfied',
    Neither: 'Neither satisfied or dissatisfied',
    Dissatisfied: 'Dissatisfied',
    VeryDissatisfied: 'Very dissatisfied',
};
