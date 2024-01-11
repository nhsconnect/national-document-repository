import { FormData } from '../../types/pages/feedbackPage/types';

const sendEmail = async (formData: FormData) => {
    // using console.log as a placeholder until we got the send email solution in place
    /* eslint-disable-next-line no-console */
    console.log(`sending feedback from user by email: ${JSON.stringify(formData)}}`);
    return { status: 200 };
};

export default sendEmail;
