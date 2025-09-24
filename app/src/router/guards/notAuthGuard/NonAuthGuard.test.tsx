import { render, waitFor } from '@testing-library/react';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import * as ReactRouter from 'react-router-dom';
import { History, createMemoryHistory } from 'history';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import NonAuthGuard from './NonAuthGuard';
import { routes } from '../../../types/generic/routes';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

const guardPage = '/';
describe('NonAuthGuard', () => {
    beforeEach(() => {
        localStorage.setItem('UserSession', '');

        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });
    it('navigates user to supplied route when user is logged in', async () => {
        const auth: Session = {
            auth: buildUserAuth(),
            isLoggedIn: true,
        };
        const history = createMemoryHistory({
            initialEntries: [guardPage],
            initialIndex: 0,
        });
        expect(history.location.pathname).toBe(guardPage);
        renderNonAuthGuard(auth, history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(routes.HOME);
        });
    });

    it('navigates user to correct page when user is not logged in', async () => {
        const auth: Session = {
            auth: null,
            isLoggedIn: false,
        };
        const history = createMemoryHistory({
            initialEntries: [guardPage],
            initialIndex: 0,
        });
        expect(history.location.pathname).toBe(guardPage);
        renderNonAuthGuard(auth, history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(guardPage);
        });
    });
});

const renderNonAuthGuard = (session: Session, history: History) => {
    render(
        <SessionProvider sessionOverride={session}>
            <ReactRouter.Router navigator={history} location={history.location}>
                <NonAuthGuard redirectRoute={routes.HOME}>
                    <div>User is not logged in</div>
                </NonAuthGuard>
            </ReactRouter.Router>
            ,
        </SessionProvider>,
    );
};
