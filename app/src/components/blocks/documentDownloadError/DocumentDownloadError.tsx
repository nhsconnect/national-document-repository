import ErrorBox from '../../layout/errorBox/ErrorBox';

function DocumentDownloadError() {
    return (
        <ErrorBox
            messageTitle={'There is a problem with the documents'}
            messageBody={'An error has occurred while preparing your download'}
            errorBoxSummaryId={'error-box-summary'}
        />
    );
}

export default DocumentDownloadError;
