import { ErrorSummary } from 'nhsuk-react-components';

type Props = {
    message?: string;
};

const ServiceError = ({ message }: Props) => {
    const serviceErrorSummaryId = 'service-error-summary';
    const defaultMessage = 'Please try again later.';

    return (
        <ErrorSummary aria-labelledby={serviceErrorSummaryId} role="alert" tabIndex={-1}>
            <ErrorSummary.Title id={serviceErrorSummaryId}>
                Sorry, the service is currently unavailable.
            </ErrorSummary.Title>
            <ErrorSummary.Body>
                <p>{message || defaultMessage}</p>
                <p>
                    Please check your internet connection. If the issue persists please contact the{' '}
                    <a
                        href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                        target="_blank"
                        rel="noreferrer"
                    >
                        NHS National Service Desk
                    </a>
                    .
                </p>
            </ErrorSummary.Body>
        </ErrorSummary>
    );
};

export default ServiceError;
