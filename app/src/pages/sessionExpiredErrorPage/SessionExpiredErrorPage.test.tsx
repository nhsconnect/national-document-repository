import { render, screen, waitFor } from '@testing-library/react';
// import ServerErrorPage from './ServerErrorPage';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { unixTimestamp } from '../../helpers/utils/createTimestamp';
import SessionExpiredErrorPage from './SessionExpiredErrorPage';
import { routes } from '../../types/generic/routes';

const mockedNavigate = jest.fn();

jest.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});
//
jest.mock('react-router', () => ({
    useNavigate: () => mockedNavigate,
    useLocation: () => jest.fn(),
}));
//
describe('ServerErrorPage', () => {
    it('render a page with a user friendly message to state that their session expired', () => {
        render(<SessionExpiredErrorPage />);

        expect(
            screen.getByRole('heading', { name: 'You have been logged out' }),
        ).toBeInTheDocument();

        expect(
            screen.getByText(
                'Your session has automatically expired following a period of inactivity. This is to protect patient security.',
            ),
        ).toBeInTheDocument();

        expect(screen.getByText('Log in again to use this service.')).toBeInTheDocument();

        expect(
            screen.getByRole('heading', {
                name: 'If this error keeps appearing',
            }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('link', {
                name: 'Contact the NHS National Service Desk',
            }),
        ).toBeInTheDocument();

        const mockInteractionId = unixTimestamp();
        expect(screen.getByText(mockInteractionId)).toBeInTheDocument();
    });

    it('navigate to start page when user click the return button', () => {
        render(<SessionExpiredErrorPage />);

        const returnButton = screen.getByRole('button', {
            name: 'Return to start and log in again',
        });
        expect(returnButton).toBeInTheDocument();

        act(() => {
            returnButton.click();
        });

        expect(mockedNavigate).toBeCalledWith(routes.START);
    });
});
