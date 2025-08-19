import { GenericError } from "../../types/pages/genericPageErrors";
import { getGenericErrorBoxErrorMessage, groupErrorsByType } from "./genericErrorMessages";

type FeedbackError = GenericError<FEEDBACK_ERROR_TYPE>;

export enum FEEDBACK_ERROR_TYPE {
  feedbackSatisfaction = 'feedbackSatisfaction',
  feedbackTextbox = 'feedbackTextbox',
  emailTextInput = 'emailTextInput',
}

export type FeedbackErrorMessageType = {
  inline: string;
  errorBox: string;
};

export const getFeedbackErrorBoxErrorMessage = (error: FeedbackError): string =>
  getGenericErrorBoxErrorMessage(error, feedbackErrorMessages);

export const groupFeedbackErrorsByType = (
    errors: FeedbackError[]
) => groupErrorsByType(
    errors,
    getFeedbackErrorBoxErrorMessage
);

type errorMessageType = { [errorType in FEEDBACK_ERROR_TYPE]: FeedbackErrorMessageType };

export const feedbackErrorMessages: errorMessageType = {
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
}
