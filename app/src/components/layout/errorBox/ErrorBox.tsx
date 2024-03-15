import { ErrorSummary } from 'nhsuk-react-components';
import { MouseEvent } from 'react';
import { UploadFilesErrors } from '../../../types/pages/UploadDocumentsPage/types';

type Props = {
    errorBoxSummaryId: string;
    messageTitle: string;
    messageBody?: string;
    messageLinkBody?: string;
    errorInputLink?: string;
    errorBody?: string;
    dataTestId?: string;
    errorOnClick?: () => void;
    errorMessageList?: UploadFilesErrors[];
};

// @ts-ignore
const ErrorBox = ({
    errorBoxSummaryId,
    errorInputLink,
    messageTitle,
    messageBody,
    messageLinkBody,
    errorBody,
    errorMessageList,
    errorOnClick,
    dataTestId,
}: Props) => {
    const hasInputLink = errorInputLink && messageLinkBody;
    const hasOnClick = errorOnClick && messageLinkBody;

    return (
        <div id="error-box" data-testid={dataTestId}>
            <ErrorSummary aria-labelledby={errorBoxSummaryId} role="alert" tabIndex={-1}>
                <ErrorSummary.Title id={errorBoxSummaryId}>{messageTitle}</ErrorSummary.Title>
                <ErrorSummary.Body>
                    <ErrorSummary.List>
                        {errorBody && (
                            <ErrorSummary.Item
                                href="#"
                                onClick={(e: MouseEvent<HTMLAnchorElement>) => {
                                    e.preventDefault();
                                }}
                            >
                                {errorBody}
                            </ErrorSummary.Item>
                        )}

                        {messageBody && <p>{messageBody}</p>}
                        {hasInputLink && (
                            <ErrorSummary.Item href={errorInputLink}>
                                <p>{messageLinkBody}</p>
                            </ErrorSummary.Item>
                        )}
                        {hasOnClick && (
                            <ErrorSummary.Item
                                data-testid="error-summary-btn"
                                href={'#'}
                                onClick={(e) => {
                                    e.preventDefault();
                                    errorOnClick();
                                }}
                            >
                                <p>{messageLinkBody}</p>
                            </ErrorSummary.Item>
                        )}
                        {errorMessageList?.map((errorItem, i) => {
                            const key = (errorItem.filename ?? '') + errorItem.error.errorBox + i;

                            return (
                                <div key={key}>
                                    <p>{errorItem.error.errorBox}</p>
                                    <ErrorSummary.Item href={'#' + errorItem.filename}>
                                        <p>{errorItem.filename}</p>
                                    </ErrorSummary.Item>
                                </div>
                            );
                        })}
                    </ErrorSummary.List>
                </ErrorSummary.Body>
            </ErrorSummary>
        </div>
    );
};

export default ErrorBox;
