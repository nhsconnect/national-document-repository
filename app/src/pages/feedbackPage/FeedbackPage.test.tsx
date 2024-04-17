import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { SATISFACTION_CHOICES } from '../../types/pages/feedbackPage/types';
import FeedbackPage from './FeedbackPage';
import sendEmail from '../../helpers/requests/sendEmail';
import { fillInForm } from '../../helpers/test/formUtils';
import HomePage from '../homePage/HomePage';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
jest.mock('../../helpers/hooks/useBaseAPIHeaders');

jest.mock('../../helpers/requests/sendEmail');
const mockSendEmail = sendEmail as jest.Mock;
jest.mock('react-router-dom', () => ({
    useNavigate: () => jest.fn(),
}));
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

    it('renders the confirmation page when the feedback form was submitted', async () => {
        render(<FeedbackPage />);

        act(() => {
            fillInForm(mockInputData);
            userEvent.click(screen.getByRole('button', { name: 'Send feedback' }));
        });

        await screen.findByText('We’ve received your feedback');
    });

    it('pass accessibility checks', async () => {
        render(<FeedbackPage />);
        const results = await runAxeTest(document.body);

        expect(results).toHaveNoViolations();
    });
});

const mockInputData = {
    feedbackContent: 'Mock feedback content',
    howSatisfied: SATISFACTION_CHOICES.VerySatisfied,
    respondentName: 'Jane Smith',
    respondentEmail: 'jane_smith@testing.com',
};
