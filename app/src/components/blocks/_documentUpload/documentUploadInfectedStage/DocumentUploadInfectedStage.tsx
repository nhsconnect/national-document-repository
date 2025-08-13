import useTitle from '../../../../helpers/hooks/useTitle';
import { useNavigate } from 'react-router';
import { routes } from '../../../../types/generic/routes';

function DocumentUploadInfectedStage() {
    const navigate = useNavigate();
    const pageHeader = "We couldn't upload your files because we found a virus";
    useTitle({ pageTitle: pageHeader });

    return (
        <>
            <h1>{pageHeader}</h1>

            <p>One or more of your files has a virus.</p>

            <p>
                To keep patient information safe and our systems secure, we've stopped the upload.
            </p>

            <p>Contact your local IT support desk for help.</p>

            <p>
                <button
                    className="govuk-link"
                    onClick={(e) => {
                        e.preventDefault();
                        navigate(routes.DOCUMENT_UPLOAD, { replace: true });
                    }}
                >
                    Go back to choose Lloyd George files to upload
                </button>
            </p>
        </>
    );
}

export default DocumentUploadInfectedStage;
