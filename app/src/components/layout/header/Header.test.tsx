import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Header from './Header';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import { routes } from '../../../types/generic/routes';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
jest.mock('../../../helpers/hooks/useRole');

const mockedUseRole = useRole as jest.Mock;

const mockedUseNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('Header', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
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
            userEvent.click(screen.getByText('Access and store digital GP records'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
            });
        });

        it('navigates to the home page when logo is clicked and user is logged in', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            renderHeaderWithRouter();

            userEvent.click(screen.getByRole('img', { name: 'NHS Logo' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
            });
        });

        it('navigates to the start page when logo is clicked and user is logged out', async () => {
            mockedUseRole.mockReturnValue(null);
            renderHeaderWithRouter();

            userEvent.click(screen.getByRole('img', { name: 'NHS Logo' }));

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
