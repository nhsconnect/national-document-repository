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

            expect(screen.getByText(/Your/i)).toBeInTheDocument();
            expect(screen.getByText(/feedback/i)).toBeInTheDocument();
            expect(screen.getByText(/will help us to improve this service./i)).toBeInTheDocument();
        });
    });
    describe('Navigation', () => {
        it.skip('renders an external  link with a feedback href', () => {
            /**
             * Remove skip once feedback link attribute has been verified by Product team
             */
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
