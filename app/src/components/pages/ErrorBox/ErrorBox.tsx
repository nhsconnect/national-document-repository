import { ErrorSummary } from 'nhsuk-react-components';

type Props = {
  errorBoxSummaryId: string;
  errorInputLink?: string;
  messageTitle: string;
  messageBody?: string;
  messageLinkBody?: string;
};

const ErrorBox = ({
  errorBoxSummaryId,
  errorInputLink,
  messageTitle,
  messageBody,
  messageLinkBody
}: Props) => {
  const isInputLink = errorInputLink && messageLinkBody;

  return (
    <ErrorSummary
      aria-labelledby={errorBoxSummaryId}
      role='alert'
      tabIndex={-1}
    >
      <ErrorSummary.Title id={errorBoxSummaryId}>
        {messageTitle}
      </ErrorSummary.Title>
      <ErrorSummary.Body>
        <ErrorSummary.List>
          {messageBody && <p>{messageBody}</p>}
          {isInputLink && (
            <ErrorSummary.Item href={errorInputLink}>
              <p>{messageLinkBody}</p>
            </ErrorSummary.Item>
          )}
        </ErrorSummary.List>
      </ErrorSummary.Body>
    </ErrorSummary>
  );
};

export default ErrorBox;
