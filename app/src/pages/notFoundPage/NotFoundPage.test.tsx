import { render, screen } from '@testing-library/react';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import NotFoundPage from './NotFoundPage';
describe('NotFoundPage', () => {
    it('renders unauthorised message', () => {
        const history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
        render(
            <ReactRouter.Router navigator={history} location={history.location}>
                <NotFoundPage />
            </ReactRouter.Router>,
        );
        expect(screen.getByText('Page not found')).toBeInTheDocument();
    });
});
