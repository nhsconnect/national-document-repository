import { render, screen } from '@testing-library/react';
import PhaseBanner from './PhaseBanner';

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

            expect(screen.getByText(/This is a new service - your/i)).toBeInTheDocument();
            expect(screen.getByText('feedback')).toBeInTheDocument();
            expect(screen.getByText(/will help us to improve it./i)).toBeInTheDocument();
        });
    });
    describe('Navigation', () => {
        it('renders an external  link with a feedback href', () => {
            render(<PhaseBanner />);
            const feedbackLink = screen.getByRole('link', {
                name: 'feedback',
            });
            expect(feedbackLink).toHaveAttribute(
                'href',
                'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
            );
            expect(feedbackLink).toHaveAttribute('target', '_blank');
        });
    });
});
