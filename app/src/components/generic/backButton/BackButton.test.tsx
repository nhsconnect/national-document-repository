import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BackButton from './BackButton';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';

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
        userEvent.click(screen.getByText('Go back'));

        await waitFor(() => {
            expect(mockUseNavigate).toHaveBeenCalledWith(-1);
        });
    });
});
