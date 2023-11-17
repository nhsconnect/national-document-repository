import { createMemoryHistory } from 'history';
import { render, screen, waitFor } from '@testing-library/react';
import * as ReactRouter from 'react-router';
import userEvent from '@testing-library/user-event';
import BackButton from './BackButton';
import { routes } from '../../../types/generic/routes';
import { endpoints } from '../../../types/generic/endpoints';
import { useBaseAPIUrl } from '../../../providers/configProvider/ConfigProvider';

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

    it('calls the login handler when clicking the back button on the upload search page', async () => {
        const test_location_prefix = useBaseAPIUrl();

        const history = createMemoryHistory({
            initialEntries: ['/', '/example'],
            initialIndex: 1,
        });

        //Override the default window.location property as it is not configurable so can't be mocked by jest
        Object.defineProperty(window, 'location', {
            configurable: true,
            enumerable: true,
            value: new URL(window.location.href),
        });

        window.location.replace = jest.fn();

        render(
            <ReactRouter.Router navigator={history} location={routes.UPLOAD_SEARCH}>
                <BackButton />
            </ReactRouter.Router>,
        );

        userEvent.click(screen.getByText('Back'));

        await waitFor(() => {
            expect(window.location.replace).toBeCalledWith(test_location_prefix + endpoints.LOGIN);
        });
    });

    it('calls the login handler when clicking the back button on the download search page', async () => {
        const test_location_prefix = useBaseAPIUrl();

        const history = createMemoryHistory({
            initialEntries: ['/', '/example'],
            initialIndex: 1,
        });

        //Override the default window.location property as it is not configurable so can't be mocked by jest
        Object.defineProperty(window, 'location', {
            configurable: true,
            enumerable: true,
            value: new URL(window.location.href),
        });

        window.location.replace = jest.fn();

        render(
            <ReactRouter.Router navigator={history} location={routes.DOWNLOAD_SEARCH}>
                <BackButton />
            </ReactRouter.Router>,
        );

        userEvent.click(screen.getByText('Back'));

        await waitFor(() => {
            expect(window.location.replace).toBeCalledWith(test_location_prefix + endpoints.LOGIN);
        });
    });
});
