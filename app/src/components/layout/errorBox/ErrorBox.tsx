import { ErrorSummary } from 'nhsuk-react-components';
import { LegacyRef, MouseEvent, JSX } from 'react';
import { groupUploadErrorsByType } from '../../../helpers/utils/fileUploadErrorMessages';
import { UploadFilesError } from '../../../types/pages/UploadDocumentsPage/types';

type Props = {
    errorBoxSummaryId: string;
    messageTitle: string;
    messageBody?: string;
    messageLinkBody?: string;
    errorInputLink?: string;
    errorBody?: string;
    dataTestId?: string;
    errorOnClick?: () => void;
    errorMessageList?: UploadFilesError[];
    scrollToRef?: LegacyRef<HTMLDivElement>;
};

type UploadErrorMessagesProps = {
    errorMessageList: UploadFilesError[];
};

function UploadErrorMessages({
    errorMessageList,
}: Readonly<UploadErrorMessagesProps>): JSX.Element {
    const uploadErrorsGrouped = groupUploadErrorsByType(errorMessageList);

    return (
        <>
            {Object.entries(uploadErrorsGrouped).map(([errorType, { linkIds, errorMessage }]) => {
                const firstFile = linkIds[0];
                return (
                    <div key={errorType}>
                        <ErrorSummary.List>
                            <ErrorSummary.Item href={'#' + firstFile} key={errorType + firstFile}>
                                {errorMessage}
                            </ErrorSummary.Item>
                        </ErrorSummary.List>
                    </div>
                );
            })}
        </>
    );
}

const ErrorBox = ({
    errorBoxSummaryId,
    messageTitle,
    messageBody,
    messageLinkBody,
    errorInputLink,
    errorBody,
    dataTestId,
    errorOnClick,
    errorMessageList,
    scrollToRef,
}: Props): JSX.Element => {
    const hasInputLink = errorInputLink && messageLinkBody;
    const hasOnClick = errorOnClick && messageLinkBody;

    return (
        <div id="error-box" data-testid={dataTestId} ref={scrollToRef}>
            <ErrorSummary aria-labelledby={errorBoxSummaryId} role="alert" tabIndex={-1}>
                <ErrorSummary.Title id={errorBoxSummaryId}>{messageTitle}</ErrorSummary.Title>
                <ErrorSummary.Body>
                    <ErrorSummary.List>
                        {errorBody && (
                            <ErrorSummary.Item
                                href="#"
                                onClick={(e: MouseEvent<HTMLAnchorElement>): void => {
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
                                data-testid="error-box-link"
                                href={'#'}
                                onClick={(e): void => {
                                    e.preventDefault();
                                    errorOnClick();
                                }}
                            >
                                <p>{messageLinkBody}</p>
                            </ErrorSummary.Item>
                        )}
                    </ErrorSummary.List>
                    {errorMessageList && (
                        <UploadErrorMessages errorMessageList={errorMessageList} />
                    )}
                </ErrorSummary.Body>
            </ErrorSummary>
        </div>
    );
};

export default ErrorBox;
