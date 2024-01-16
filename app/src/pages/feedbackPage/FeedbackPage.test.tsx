import { render, screen } from '@testing-library/react';
import FeedbackPage from './FeedbackPage';
import sendEmail from '../../helpers/requests/sendEmail';

jest.mock('../../helpers/requests/sendEmail');
const mockSendEmail = sendEmail as jest.Mock;

describe('<FeedbackPage />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockSendEmail.mockReturnValueOnce(Promise.resolve());
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the feedback form initially', () => {
        render(<FeedbackPage />);

        expect(
            screen.getByText('Give feedback on accessing Lloyd George digital patient records'),
        ).toBeInTheDocument();
    });

    it.skip('renders the confirmation page when the feedback form was submitted', async () => {
        // to be implemented in PRMDR-578
    });
});
