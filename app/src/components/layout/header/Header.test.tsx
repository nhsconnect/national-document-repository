import { render, screen, waitFor } from '@testing-library/react';
import * as ReactRouter from 'react-router';
import userEvent from '@testing-library/user-event';
import Header from './Header';
import { createMemoryHistory } from 'history';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';

describe('Header', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('displays the header', () => {
            const history = createMemoryHistory({
                initialEntries: ['/', '/example'],
                initialIndex: 1,
            });

            renderHeaderWithRouter(history);

            expect(screen.getByRole('banner')).toBeInTheDocument();
        });
    });

    describe('Navigating', () => {
        it('navigates to the home page when header is clicked', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/', '/example'],
                initialIndex: 1,
            });

            renderHeaderWithRouter(history);

            expect(history.location.pathname).toBe('/example');

            userEvent.click(screen.getByText('Inactive Patient Record Administration'));

            await waitFor(() => {
                expect(history.location.pathname).toBe('/');
            });
        });

        it('navigates to the home page when logo is clicked', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/', '/example'],
                initialIndex: 1,
            });

            renderHeaderWithRouter(history);
            expect(history.location.pathname).toBe('/example');

            userEvent.click(screen.getByRole('img', { name: 'NHS Logo' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe('/');
            });
        });
    });

    const renderHeaderWithRouter = (
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 1,
        }),
        authOverride?: Partial<Session>,
    ) => {
        const auth: Session = {
            auth: buildUserAuth(),
            isLoggedIn: true,
            ...authOverride,
        };
        render(
            <ReactRouter.Router navigator={history} location={'/'}>
                <SessionProvider sessionOverride={auth}>
                    <Header />
                </SessionProvider>
            </ReactRouter.Router>,
        );
    };
});
