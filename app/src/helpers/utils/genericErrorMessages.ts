import { GenericError } from "../../types/pages/UploadDocumentsPage/types";

export type ErrorMessageMap<T extends string> = Record<
  T,
  {
    inline: string;
    errorBox: string;
  }
>;

export function getGenericErrorBoxErrorMessage<T extends string>(
  error: GenericError<T>,
  messageMap: ErrorMessageMap<T>
): string {
  return messageMap[error.error].errorBox;
}


export function groupErrorsByType<T extends string>(
  errors: GenericError<T>[],
  getMessage: (error: GenericError<T>) => string
): Partial<Record<T, { linkIds: string[]; errorMessage: string }>> {
  const result: Partial<Record<T, { linkIds: string[]; errorMessage: string }>> = {};

  errors.forEach((errorItem) => {
    const { error, linkId = '' } = errorItem;
    const errorMessage = getMessage(errorItem);

    if (!result[error]) {
      result[error] = { linkIds: [linkId], errorMessage };
    } else {
      result[error]!.linkIds.push(linkId);
    }
  });

  return result;
}
