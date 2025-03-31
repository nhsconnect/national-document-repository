import { act, render, screen, waitFor } from '@testing-library/react';
import SessionExpiredErrorPage from './SessionExpiredErrorPage';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import { endpoints } from '../../types/generic/endpoints';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import SessionProvider from '../../providers/sessionProvider/SessionProvider';
import { History, createMemoryHistory } from 'history';
import * as ReactRouter from 'react-router-dom';

const mockNavigate = jest.fn();

jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    Link: (props: ReactRouter.LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

const originalWindowLocation = window.location;
const mockLocationReplace = jest.fn();
const mockUseBaseUrl = useBaseAPIUrl as jest.Mock;

let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('SessionExpiredErrorPage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
    });
    afterAll(() => {
        Object.defineProperty(window, 'location', {
            value: originalWindowLocation,
        });
    });

    it('render a page with a user friendly message to state that their session expired', async () => {
        await renderPage(history);

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
        await renderPage(history);
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

        await renderPage(history);

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

    const renderPage = async (history: History) => {
        return await act(async () => {
            return render(
                <SessionProvider sessionOverride={{ isLoggedIn: true }}>
                    <ReactRouter.Router navigator={history} location={history.location}>
                        <SessionExpiredErrorPage />
                    </ReactRouter.Router>
                </SessionProvider>,
            );
        });
    };
});
