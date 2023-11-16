import { createMemoryHistory } from 'history';
import { render, screen, waitFor } from '@testing-library/react';
import * as ReactRouter from 'react-router';
import userEvent from '@testing-library/user-event';
import BackButton from './BackButton';

describe('BackButton', () => {
    it('navigates to previous page when clicking the back buttonand not on the search pages', async () => {
        const history = createMemoryHistory({
            initialEntries: ['/', '/example'],
            initialIndex: 1,
        });

        render(
            <ReactRouter.Router navigator={history} location={'/example'}>
                <BackButton />
            </ReactRouter.Router>,
        );

        userEvent.click(screen.getByText('Back'));

        await waitFor(() => {
            expect(history.location.pathname).toBe('/');
        });
    });

    it.skip('navigates calls the login handler when clicking the back button on a patient search page', async () => {
        const history = createMemoryHistory({
            initialEntries: [],
        });

        render(
            <ReactRouter.Router navigator={history} location={'exampleBaseUrl/search'}>
                <BackButton />
            </ReactRouter.Router>,
        );

        userEvent.click(screen.getByText('Back'));

        await waitFor(() => {
            expect(history.location.pathname).toBe('/');
        });
    });
});
