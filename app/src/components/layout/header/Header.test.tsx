import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Header from './Header';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import { routes } from '../../../types/generic/routes';

const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
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
        it('navigates to the home page when header is clicked', async () => {
            renderHeaderWithRouter();

            userEvent.click(screen.getByText('Access and store digital GP records'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
            });
        });

        it('navigates to the home page when logo is clicked', async () => {
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
