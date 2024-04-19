import pageTitle from '../../../helpers/hooks/useTitle';

function FeedbackConfirmation() {
    const pageHeader = 'We’ve received your feedback';
    pageTitle({ pageTitle: 'Feedback sent' });
    return (
        <>
            <h1>{pageHeader}</h1>
            <p>If you have left your details, our team will contact you soon.</p>
            <p>You can now close this window.</p>
        </>
    );
}

export default FeedbackConfirmation;
