import { act, render, screen } from '@testing-library/react';
import SessionProvider, { useSessionContext } from './SessionProvider';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
const loggedIn = {
    auth: buildUserAuth(),
    isLoggedIn: true,
};
const loggedOut = {
    auth: null,
    isLoggedIn: false,
};
describe('SessionProvider', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('is able to set and retrieve auth data when user has logged in', async () => {
        renderSessionProvider();
        expect(screen.getByText('isLoggedIn - false')).toBeInTheDocument();
        expect(screen.getByText('authCode - undefined')).toBeInTheDocument();
        act(() => {
            userEvent.click(screen.getByText('Log in'));
        });

        expect(screen.getByText('isLoggedIn - true')).toBeInTheDocument();

        expect(
            screen.getByText(`authCode - ${loggedIn.auth.authorisation_token}`),
        ).toBeInTheDocument();
    });

    it('is able to delete auth data when user has logged out', async () => {
        renderSessionProvider();
        act(() => {
            userEvent.click(screen.getByText('Log in'));
        });
        expect(screen.getByText('isLoggedIn - true')).toBeInTheDocument();

        expect(
            screen.getByText(`authCode - ${loggedIn.auth.authorisation_token}`),
        ).toBeInTheDocument();

        act(() => {
            userEvent.click(screen.getByText('Log out'));
        });
        expect(screen.getByText('isLoggedIn - false')).toBeInTheDocument();

        expect(screen.getByText('authCode - undefined')).toBeInTheDocument();
    });
});

const TestApp = () => {
    const [session, setSession] = useSessionContext();

    return (
        <>
            <div>
                <h1>Actions</h1>
                <div onClick={() => setSession(loggedIn)}>Log in</div>
                <div onClick={() => setSession(loggedOut)}>Log out</div>
            </div>
            <div>
                <h1>Details</h1>
                <span>isLoggedIn - {`${session.isLoggedIn}`}</span>
                <span>authCode - {`${session.auth?.authorisation_token}`}</span>
            </div>
        </>
    );
};

const renderSessionProvider = () => {
    render(
        <SessionProvider>
            <TestApp />
        </SessionProvider>,
    );
};
