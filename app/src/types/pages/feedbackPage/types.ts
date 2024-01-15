export type FormData = Record<FORM_FIELDS, string>;

export enum FORM_FIELDS {
    FeedbackContent = 'feedbackContent',
    HowSatisfied = 'howSatisfied',
    RespondentName = 'respondentName',
    RespondentEmail = 'respondentEmail',
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
