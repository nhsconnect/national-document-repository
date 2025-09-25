import { render, screen } from '@testing-library/react';
import PhaseBanner from './PhaseBanner';
import { routes } from '../../../types/generic/routes';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import { LinkProps } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} href={props.to as string} role="link" />,
}));

describe('PhaseBanner', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        window.localStorage.clear();
    });
    afterEach(() => {
        vi.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders PhaseBanner with content', () => {
            renderComponent();

            expect(screen.getByText('New service')).toBeInTheDocument();

            expect(screen.getByText(/Your/i)).toBeInTheDocument();
            expect(screen.getByText(/feedback/i)).toBeInTheDocument();
            expect(screen.getByText(/will help us to improve this service./i)).toBeInTheDocument();
        });
    });
    describe('Navigation', () => {
        it('renders a link to the feedback form page if user is logged in', () => {
            renderComponent({ isLoggedIn: true });
            const feedbackLink = screen.getByRole('link', {
                name: 'feedback - this link will open in a new tab',
            });

            expect(feedbackLink).toHaveAttribute('href', routes.FEEDBACK);
            expect(feedbackLink).toHaveAttribute('target', '_blank');
        });

        it('does not render a link if user is not logged in', () => {
            renderComponent({ isLoggedIn: false });
            expect(screen.queryByRole('link', { name: 'feedback' })).not.toBeInTheDocument();
        });
    });
});

const renderComponent = (sessionOverride: Partial<Session> = { isLoggedIn: true }) => {
    render(
        <SessionProvider sessionOverride={sessionOverride}>
            <PhaseBanner />
        </SessionProvider>,
    );
};
