import { SUBMISSION_STAGE } from '../../types/pages/feedbackPage/types';
import React, { useState } from 'react';
import FeedbackForm from '../../components/blocks/feedbackForm/FeedbackForm';

function FeedbackPage() {
    const [stage, setStage] = useState(SUBMISSION_STAGE.NotSubmitted);

    // to render confirmation screen if SUBMISSION_STAGE is successful
    return <FeedbackForm stage={stage} setStage={setStage} />;
}

export default FeedbackPage;
