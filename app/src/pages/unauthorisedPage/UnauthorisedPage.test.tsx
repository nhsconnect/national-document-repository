import { act, render, screen, waitFor } from '@testing-library/react';
import UnauthorisedPage from './UnauthorisedPage';
import { LinkProps } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { routes } from '../../types/generic/routes';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { describe, expect, it, vi } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockedUseNavigate,
}));
vi.mock('../../helpers/hooks/useBaseAPIUrl');

describe('UnauthorisedPage', () => {
    describe('Rendering', () => {
        it('renders unauthorised message', () => {
            render(<UnauthorisedPage />);
            expect(screen.getByText('Unauthorised access')).toBeInTheDocument();
        });

        it('renders a return home link', () => {
            render(<UnauthorisedPage />);
            expect(
                screen.getByRole('link', {
                    name: 'Return home',
                }),
            ).toBeInTheDocument();
        });

        it('pass accessibility checks', async () => {
            render(<UnauthorisedPage />);
            const results = await runAxeTest(document.body);

            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates user to home page when return home is clicked', async () => {
            render(<UnauthorisedPage />);
            const returnHomeLink = screen.getByRole('link', {
                name: 'Return home',
            });
            expect(returnHomeLink).toBeInTheDocument();
            act(() => {
                userEvent.click(returnHomeLink);
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.START);
            });
        });
    });
});
