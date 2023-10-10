import { render, screen } from '@testing-library/react';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import AuthErrorPage from './AuthErrorPage';

describe('AuthErrorPage', () => {
    it('renders unauthorised message', () => {
        const history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
        render(
            <ReactRouter.Router navigator={history} location={history.location}>
                <AuthErrorPage />
            </ReactRouter.Router>,
        );
        expect(screen.getByText('You have been logged out')).toBeInTheDocument();
    });

    //TODO: spinner test when log in clicked
});
