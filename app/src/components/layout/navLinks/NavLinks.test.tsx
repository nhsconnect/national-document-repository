import { render, screen } from '@testing-library/react';
import NavLinks from './NavLinks';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';

describe('NavLinks', () => {
    const oldWindowLocation = window.location;

    afterEach(() => {
        jest.clearAllMocks();
        window.location = oldWindowLocation;
    });

    it('renders a navlink that returns to app home', () => {
        renderNavWithRouter();

        expect(screen.getByRole('link', { name: 'Home' })).toBeInTheDocument();
    });
});

const renderNavWithRouter = (authOverride?: Partial<Session>) => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
        ...authOverride,
    };
    const history = createMemoryHistory({
        initialEntries: ['/'],
        initialIndex: 1,
    });
    render(
        <ReactRouter.Router navigator={history} location={'/'}>
            <SessionProvider sessionOverride={auth}>
                <NavLinks />
            </SessionProvider>
        </ReactRouter.Router>,
    );
};
