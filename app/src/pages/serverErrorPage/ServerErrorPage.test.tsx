import { render, screen, waitFor } from '@testing-library/react';
import ServerErrorPage from './ServerErrorPage';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { unixTimestamp } from '../../helpers/utils/createTimestamp';
import exp from 'node:constants';

const mockedUseNavigate = jest.fn();

jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
    useLocation: () => jest.fn(),
}));

describe('ServerErrorPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders page content with default error message when there are no url params', () => {
            const mockErrorCode = '';
            const mockInteractionId = unixTimestamp();
            const mockEncoded = btoa(JSON.stringify([mockErrorCode, mockInteractionId]));
            jest.spyOn(URLSearchParams.prototype, 'get').mockReturnValue(mockEncoded);

            render(<ServerErrorPage />);

            expect(
                screen.getByRole('heading', {
                    name: 'Sorry, there is a problem with the service',
                }),
            ).toBeInTheDocument();
            expect(screen.getByText('An unknown error has occurred.')).toBeInTheDocument();
            expect(
                screen.getByText(
                    "Try again by returning to the previous page. You'll need to enter any information you submitted again.",
                ),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', {
                    name: 'Return to previous page',
                }),
            ).toBeInTheDocument();
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
            expect(screen.getByText(mockInteractionId)).toBeInTheDocument();
        });

        it('renders page content with error message and id when there is a valid error code with interaction id', () => {
            const mockErrorCode = 'CDR_5001';
            const mockInteractionId = '000-000';
            const mockEncoded = btoa(JSON.stringify([mockErrorCode, mockInteractionId]));
            jest.spyOn(URLSearchParams.prototype, 'get').mockReturnValue(mockEncoded);
            render(<ServerErrorPage />);

            expect(
                screen.getByRole('heading', {
                    name: 'Sorry, there is a problem with the service',
                }),
            ).toBeInTheDocument();
            expect(screen.getByText('Internal error')).toBeInTheDocument();
            expect(screen.queryByText('An unknown error has occurred.')).not.toBeInTheDocument();
            expect(screen.getByText(mockInteractionId)).toBeInTheDocument();
        });

        it('renders page content with default error message and id when there is an invalid error code', () => {
            const mockErrorCode = 'XXX';
            const mockInteractionId = '000-000';
            const mockEncoded = btoa(JSON.stringify([mockErrorCode, mockInteractionId]));
            jest.spyOn(URLSearchParams.prototype, 'get').mockReturnValue(mockEncoded);
            render(<ServerErrorPage />);

            expect(
                screen.getByRole('heading', {
                    name: 'Sorry, there is a problem with the service',
                }),
            ).toBeInTheDocument();
            expect(screen.getByText('An unknown error has occurred.')).toBeInTheDocument();
            expect(screen.getByText(mockInteractionId)).toBeInTheDocument();
            expect(screen.queryByText(mockErrorCode)).not.toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates user to previous page when return home is clicked', async () => {
            const mockErrorCode = 'XXX';
            const mockInteractionId = '000-000';
            const mockEncoded = btoa(JSON.stringify([mockErrorCode, mockInteractionId]));
            jest.spyOn(URLSearchParams.prototype, 'get').mockReturnValue(mockEncoded);

            render(<ServerErrorPage />);
            const returnButtonLink = screen.getByRole('button', {
                name: 'Return to previous page',
            });
            expect(returnButtonLink).toBeInTheDocument();
            act(() => {
                userEvent.click(returnButtonLink);
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(-2);
            });
        });
    });
});
