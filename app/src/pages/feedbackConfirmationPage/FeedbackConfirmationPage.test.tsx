import { render, screen } from '@testing-library/react';
import FeedbackConfirmationPage from './FeedbackConfirmationPage';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

describe('<FeedbackConfirmationPage />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header and content', () => {
        render(<FeedbackConfirmationPage />);

        expect(
            screen.getByRole('heading', { name: 'We’ve received your feedback' }),
        ).toBeInTheDocument();

        const contentStrings = [
            'If you have left your details, our team will contact you soon.',
            'You can now close this window.',
        ];
        contentStrings.forEach((s) => {
            expect(screen.getByText(s)).toBeInTheDocument();
        });
    });

    it('pass accessibility checks at confirmation screen', async () => {
        render(<FeedbackConfirmationPage />);

        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });
});
