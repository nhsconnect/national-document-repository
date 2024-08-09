import { act, render, screen, waitFor } from '@testing-library/react';
import { LinkProps } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { routes } from '../../types/generic/routes';
import UnauthorisedLoginPage from './UnauthorisedLoginPage';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

const mockedUseNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));
jest.mock('../../helpers/hooks/useBaseAPIUrl');

describe('UnauthorisedLoginPage', () => {
    describe('Rendering', () => {
        it('renders unauthorised message', () => {
            render(<UnauthorisedLoginPage />);
            expect(screen.getByText('Your account cannot access this service')).toBeInTheDocument();
        });

        it('renders unauthorised page content', () => {
            render(<UnauthorisedLoginPage />);

            const contentStrings = [
                'Who can access this service',
                'In order to keep patient information safe, only authorised accounts can access this service',
                'This includes:',
                'GP practice staff who work at the practice the patient is registered with who have one of these roles on their smart cards:',
                'GP Admin Role: R8010, R8013, R1790, R8008',
                'GP Clinical Role: R8000',
                'PCSE staff where a patient does not have an active registration',
                "If you don't have access and feel you should have, please contact your local Registration Authority",
            ];

            contentStrings.forEach((string) => {
                expect(screen.getByText(string)).toBeInTheDocument();
            });
        });

        it('renders a return home button', () => {
            render(<UnauthorisedLoginPage />);
            expect(
                screen.getByRole('button', {
                    name: 'Return to start page',
                }),
            ).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates user to home page when return home is clicked', async () => {
            render(<UnauthorisedLoginPage />);
            const returnHomeLink = screen.getByRole('button', {
                name: 'Return to start page',
            });
            expect(returnHomeLink).toBeInTheDocument();
            act(() => {
                userEvent.click(returnHomeLink);
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.START);
            });
        });
    });

    it('pass accessibility checks', async () => {
        render(<UnauthorisedLoginPage />);
        const results = await runAxeTest(document.body);

        expect(results).toHaveNoViolations();
    });
});
