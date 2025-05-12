import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Header from './Header';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import { routes } from '../../../types/generic/routes';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../helpers/hooks/useRole');

const mockedUseRole = useRole as Mock;

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('Header', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('displays the header', () => {
            renderHeaderWithRouter();

            expect(screen.getByRole('banner')).toBeInTheDocument();
        });
    });

    describe('Navigating', () => {
        it('navigates to the home page when header is clicked and user is logged in', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            renderHeaderWithRouter();
            userEvent.click(screen.getByText('Access and store digital patient documents'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
            });
        });

        it('navigates to the home page when logo is clicked and user is logged in', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            renderHeaderWithRouter();

            userEvent.click(screen.getByTestId('nhs-header-logo'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
            });
        });

        it('navigates to the start page when logo is clicked and user is logged out', async () => {
            mockedUseRole.mockReturnValue(null);
            renderHeaderWithRouter();

            userEvent.click(screen.getByTestId('nhs-header-logo'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.START);
            });
        });
    });

    const renderHeaderWithRouter = () => {
        const auth: Session = {
            auth: buildUserAuth(),
            isLoggedIn: true,
        };
        render(
            <SessionProvider sessionOverride={auth}>
                <Header />
            </SessionProvider>,
        );
    };
});
