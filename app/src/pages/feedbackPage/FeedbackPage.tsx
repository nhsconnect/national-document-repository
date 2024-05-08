import { SUBMISSION_STAGE } from '../../types/pages/feedbackPage/types';
import React, { useState } from 'react';
import FeedbackForm from '../../components/blocks/_feedback/feedbackForm/FeedbackForm';
import FeedbackConfirmation from '../../components/blocks/_feedback/feedbackConfirmation/FeedbackConfirmation';

function FeedbackPage() {
    const [stage, setStage] = useState(SUBMISSION_STAGE.NotSubmitted);

    return stage === SUBMISSION_STAGE.Successful ? (
        <FeedbackConfirmation />
    ) : (
        <FeedbackForm stage={stage} setStage={setStage} />
    );
}

export default FeedbackPage;
