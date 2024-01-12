import { SUBMIT_STAGE } from '../../types/pages/feedbackPage/types';
import React, { useState } from 'react';
import FeedbackForm from '../../components/blocks/feedbackForm/FeedbackForm';

function FeedbackPage() {
    const [stage, setStage] = useState(SUBMIT_STAGE.NotSubmitted);

    return <FeedbackForm stage={stage} setStage={setStage} />;
}

export default FeedbackPage;
