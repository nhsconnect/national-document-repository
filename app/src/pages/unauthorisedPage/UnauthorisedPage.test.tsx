import { render, screen } from '@testing-library/react';
import * as ReactRouter from 'react-router';
import UnauthorisedPage from './UnauthorisedPage';
import { createMemoryHistory } from 'history';

describe('UnauthorisedPage', () => {
    it('renders unauthorised message', () => {
        const history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
        render(
            <ReactRouter.Router navigator={history} location={history.location}>
                <UnauthorisedPage />
            </ReactRouter.Router>,
        );
        expect(screen.getByText('Unauthorised access')).toBeInTheDocument();
    });
});
