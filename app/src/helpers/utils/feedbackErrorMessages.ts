export enum FEEDBACK_ERROR_TYPE {
  feedbackSatisfaction = 'feedbackSatisfaction',
  feedbackTextbox = 'feedbackTextbox',
  emailTextInput = 'emailTextInput',
}

export type FeedbackErrorMessageType = {
  inline: string;
  errorBox: string;
};

export const feedbackErrorMessages: Record<FEEDBACK_ERROR_TYPE, FeedbackErrorMessageType> = {
  feedbackSatisfaction: {
    inline: 'Select an option',
    errorBox: 'Select an option',
  },
  feedbackTextbox: {
    inline: 'Enter your feedback',
    errorBox: 'Enter your feedback',
  },
  emailTextInput: {
    inline: 'Enter a valid email address',
    errorBox: 'Enter a valid email address',
  },
};
