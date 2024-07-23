import { ErrorSummary } from 'nhsuk-react-components';
import { MouseEvent } from 'react';
import { UploadFilesErrors } from '../../../types/pages/UploadDocumentsPage/types';
import { groupUploadErrorsByType } from '../../../helpers/utils/fileUploadErrorMessages';

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

type UploadErrorMessagesProps = {
    errorMessageList: UploadFilesErrors[];
};

function UploadErrorMessages({ errorMessageList }: Readonly<UploadErrorMessagesProps>) {
    const uploadErrorsGrouped = groupUploadErrorsByType(errorMessageList);

    return (
        <>
            {Object.entries(uploadErrorsGrouped).map(([errorType, { filenames, errorMessage }]) => (
                <div key={errorType}>
                    <p>{errorMessage}</p>
                    <ErrorSummary.List>
                        {filenames.map((filename) => (
                            <ErrorSummary.Item href={'#' + filename} key={errorType + filename}>
                                {filename}
                            </ErrorSummary.Item>
                        ))}
                    </ErrorSummary.List>
                </div>
            ))}
        </>
    );
}

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
                                data-testid="error-box-link"
                                href={'#'}
                                onClick={(e) => {
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
