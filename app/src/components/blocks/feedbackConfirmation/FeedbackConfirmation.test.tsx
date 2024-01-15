import { render, screen } from '@testing-library/react';
import FeedbackConfirmation from './FeedbackConfirmation';

describe('<FeedbackConfirmation />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header and content', () => {
        render(<FeedbackConfirmation />);

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
});
