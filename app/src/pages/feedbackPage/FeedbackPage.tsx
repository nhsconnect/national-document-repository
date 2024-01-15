import { SUBMISSION_STAGE } from '../../types/pages/feedbackPage/types';
import React, { useState } from 'react';
import FeedbackForm from '../../components/blocks/feedbackForm/FeedbackForm';
import FeedbackConfirmation from '../../components/blocks/feedbackConfirmation/FeedbackConfirmation';

function FeedbackPage() {
    const [stage, setStage] = useState(SUBMISSION_STAGE.NotSubmitted);

    // to render confirmation screen if SUBMISSION_STAGE is successful
    return stage === SUBMISSION_STAGE.Successful ? (
        <FeedbackConfirmation />
    ) : (
        <FeedbackForm stage={stage} setStage={setStage} />
    );
}

export default FeedbackPage;
