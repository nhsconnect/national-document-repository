import { act, render, screen, waitFor } from '@testing-library/react';
import SessionExpiredErrorPage from './SessionExpiredErrorPage';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import { endpoints } from '../../types/generic/endpoints';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../helpers/hooks/useBaseAPIUrl');

const originalWindowLocation = window.location;
const mockLocationReplace = vi.fn();
const mockUseBaseUrl = useBaseAPIUrl as Mock;

describe('SessionExpiredErrorPage', () => {
    afterAll(() => {
        Object.defineProperty(window, 'location', {
            value: originalWindowLocation,
        });
    });

    it('render a page with a user friendly message to state that their session expired', () => {
        render(<SessionExpiredErrorPage />);

        expect(
            screen.getByRole('heading', { name: 'We signed you out due to inactivity' }),
        ).toBeInTheDocument();

        expect(
            screen.getByText(
                "This is to protect your information. You'll need to enter any information you submitted again.",
            ),
        ).toBeInTheDocument();
    });

    it('pass accessibility checks', async () => {
        render(<SessionExpiredErrorPage />);
        const results = await runAxeTest(document.body);

        expect(results).toHaveNoViolations();
    });

    it('move to login endpoint when user click the button', async () => {
        const mockBackendUrl = 'http://localhost/mock_url/';
        mockUseBaseUrl.mockReturnValue(mockBackendUrl);

        Object.defineProperty(window, 'location', {
            value: {
                replace: mockLocationReplace,
            },
        });

        render(<SessionExpiredErrorPage />);

        const signBackInButton = screen.getByRole('button', {
            name: 'Sign back in',
        });
        expect(signBackInButton).toBeInTheDocument();

        act(() => {
            signBackInButton.click();
        });

        await waitFor(() =>
            expect(mockLocationReplace).toBeCalledWith(mockBackendUrl + endpoints.LOGIN),
        );
    });
});
