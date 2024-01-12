import { render, screen } from '@testing-library/react';
import PhaseBanner from './PhaseBanner';
import { routes } from '../../../types/generic/routes';

describe('PhaseBanner', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders PhaseBanner with content', () => {
            render(<PhaseBanner />);

            expect(screen.getByText('New Service')).toBeInTheDocument();

            expect(screen.getByText(/Your/i)).toBeInTheDocument();
            expect(screen.getByText(/feedback/i)).toBeInTheDocument();
            expect(screen.getByText(/will help us to improve this service./i)).toBeInTheDocument();
        });
    });
    describe('Navigation', () => {
        it('renders a link to the feedback form page', () => {
            render(<PhaseBanner />);
            const feedbackLink = screen.getByRole('link', {
                name: 'feedback',
            });

            expect(feedbackLink).toHaveAttribute('href', routes.FEEDBACK);
            expect(feedbackLink).toHaveAttribute('target', '_blank');
        });
    });
});
