import { render, screen, waitFor } from '@testing-library/react';
import ServerErrorPage from './ServerErrorPage';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';

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
        it('renders page content with default error message and id', () => {
            render(<ServerErrorPage />);

            expect(
                screen.getByRole('heading', {
                    name: 'Sorry, there is a problem with the service',
                }),
            ).toBeInTheDocument();
            expect(screen.getByText('Ulaanbaatar')).toBeInTheDocument();
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
            expect(screen.getByText('111111')).toBeInTheDocument();
        });

        it('renders page content with error message and id', () => {
            jest.spyOn(URLSearchParams.prototype, 'get').mockReturnValue('CDR_5001');
            render(<ServerErrorPage />);

            expect(
                screen.getByRole('heading', {
                    name: 'Sorry, there is a problem with the service',
                }),
            ).toBeInTheDocument();
            expect(screen.getByText('Internal error')).toBeInTheDocument();
            expect(screen.queryByText('Ulaanbaatar')).not.toBeInTheDocument();
            expect(screen.getByText('CDR_5001')).toBeInTheDocument();
            expect(screen.queryByText('111111')).not.toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates user to previous page when return home is clicked', async () => {
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
