import { SUBMISSION_STAGE } from '../../types/pages/feedbackPage/types';
import React, { useState } from 'react';
import FeedbackForm from '../../components/blocks/feedbackForm/FeedbackForm';
import FeedbackConfirmation from '../../components/blocks/feedbackConfirmation/FeedbackConfirmation';
import PageTitle from '../../components/layout/pageTitle/PageTitle';

function FeedbackPage() {
    const [stage, setStage] = useState(SUBMISSION_STAGE.NotSubmitted);
    PageTitle({ pageTitle: 'Feedback' });

    return stage === SUBMISSION_STAGE.Successful ? (
        <FeedbackConfirmation />
    ) : (
        <FeedbackForm stage={stage} setStage={setStage} />
    );
}

export default FeedbackPage;
