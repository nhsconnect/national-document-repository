import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BackButton from './BackButton';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../helpers/hooks/useBaseAPIUrl');
const mockUseBaseAPIUrl = useBaseAPIUrl as Mock;
const mockUseNavigate = vi.fn();
let mockPathname = { pathname: '' };
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockUseNavigate,
    useLocation: () => mockPathname,
}));
const testUrl = '/test';

describe('BackButton', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockUseBaseAPIUrl.mockReturnValue(testUrl);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('navigates to previous page when clicking the back button and not on the search pages', async () => {
        mockPathname = { pathname: testUrl };

        render(<BackButton />);
        userEvent.click(screen.getByText('Go back'));

        await waitFor(() => {
            expect(mockUseNavigate).toHaveBeenCalledWith(-1);
        });
    });

    it('navigates to specified location when the "toLocation" property is defined', async () => {
        render(<BackButton toLocation="/specified-location" />);
        userEvent.click(screen.getByText('Go back'));

        await waitFor(() => {
            expect(mockUseNavigate).toHaveBeenCalledWith('/specified-location');
        });
    });

    it('displays default back link text when "backLinkText" is not provided', async () => {
        render(<BackButton toLocation="/specified-location" />);
        expect(screen.getByText('Go back')).toBeInTheDocument();
    });

    it('displays custom back link text when "backLinkText" is defined', async () => {
        render(<BackButton backLinkText="navigate to ..." />);
        expect(screen.getByText('navigate to ...')).toBeInTheDocument();
    });
});
