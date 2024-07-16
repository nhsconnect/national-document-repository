import { render, waitFor } from '@testing-library/react';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import * as ReactRouter from 'react-router-dom';
import { History, createMemoryHistory } from 'history';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import AuthGuard from './AuthGuard';
import { routes } from '../../../types/generic/routes';

const guardPage = '/profile';
describe('AuthGuard', () => {
    beforeEach(() => {
        sessionStorage.setItem('UserSession', '');

        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('navigates user to unauthorised when user is not logged in', async () => {
        const auth: Session = {
            auth: null,
            isLoggedIn: false,
        };
        const history = createMemoryHistory({
            initialEntries: [guardPage],
            initialIndex: 0,
        });
        expect(history.location.pathname).toBe(guardPage);
        renderAuthGuard(auth, history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(routes.UNAUTHORISED);
        });
    });

    it('navigates user to correct page when user is logged in', async () => {
        const auth: Session = {
            auth: buildUserAuth(),
            isLoggedIn: true,
        };
        const history = createMemoryHistory({
            initialEntries: [guardPage],
            initialIndex: 0,
        });
        expect(history.location.pathname).toBe(guardPage);
        renderAuthGuard(auth, history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(guardPage);
        });
    });
});

const renderAuthGuard = (session: Session, history: History) => {
    render(
        <SessionProvider sessionOverride={session}>
            <ReactRouter.Router navigator={history} location={history.location}>
                <AuthGuard>
                    <div>User is logged in</div>
                </AuthGuard>
            </ReactRouter.Router>
            ,
        </SessionProvider>,
    );
};
