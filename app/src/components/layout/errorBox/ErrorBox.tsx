import { ErrorSummary } from 'nhsuk-react-components';

type Props = {
    errorBoxSummaryId: string;
    messageTitle: string;
    messageBody?: string;
    messageLinkBody?: string;
    errorInputLink?: string;
};

// @ts-ignore
const ErrorBox = ({
    errorBoxSummaryId,
    errorInputLink,
    messageTitle,
    messageBody,
    messageLinkBody,
}: Props) => {
    const hasInputLink = errorInputLink && messageLinkBody;
    return (
        <ErrorSummary aria-labelledby={errorBoxSummaryId} role="alert" tabIndex={-1}>
            <ErrorSummary.Title id={errorBoxSummaryId}>{messageTitle}</ErrorSummary.Title>
            <ErrorSummary.Body>
                <ErrorSummary.List>
                    {messageBody && <p>{messageBody}</p>}
                    {hasInputLink && (
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
