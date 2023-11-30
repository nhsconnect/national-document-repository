import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BackButton from './BackButton';
import { endpoints } from '../../../types/generic/endpoints';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import { routes } from '../../../types/generic/routes';

jest.mock('../../../helpers/hooks/useBaseAPIUrl');
const mockUseBaseAPIUrl = useBaseAPIUrl as jest.Mock;
const mockUseNavigate = jest.fn();
let mockPathname = { pathname: '' };
jest.mock('react-router', () => ({
    useNavigate: () => mockUseNavigate,
    useLocation: () => mockPathname,
}));
const testUrl = '/test';

describe('BackButton', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockUseBaseAPIUrl.mockReturnValue(testUrl);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('navigates to previous page when clicking the back button and not on the search pages', async () => {
        mockPathname = { pathname: testUrl };

        render(<BackButton />);
        userEvent.click(screen.getByText('Back'));

        await waitFor(() => {
            expect(mockUseNavigate).toHaveBeenCalledWith(-1);
        });
    });

    it('calls the login handler when clicking the back button on the upload search page', async () => {
        mockPathname = { pathname: routes.UPLOAD_SEARCH };
        //Override the default window.location property as it is not configurable so can't be mocked by jest
        Object.defineProperty(window, 'location', {
            configurable: true,
            enumerable: true,
            value: new URL(window.location.href),
        });

        window.location.replace = jest.fn();
        render(<BackButton />);

        userEvent.click(screen.getByText('Back'));

        await waitFor(() => {
            expect(window.location.replace).toBeCalledWith(testUrl + endpoints.LOGIN);
        });
    });

    it('calls the login handler when clicking the back button on the download search page', async () => {
        //Override the default window.location property as it is not configurable so can't be mocked by jest
        Object.defineProperty(window, 'location', {
            configurable: true,
            enumerable: true,
            value: new URL(window.location.href),
        });

        window.location.replace = jest.fn();
        mockPathname = { pathname: routes.DOWNLOAD_SEARCH };

        render(<BackButton />);

        userEvent.click(screen.getByText('Back'));

        await waitFor(() => {
            expect(window.location.replace).toBeCalledWith(testUrl + endpoints.LOGIN);
        });
    });
});
