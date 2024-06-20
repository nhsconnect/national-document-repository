import { render, screen, waitFor } from '@testing-library/react';
import UnauthorisedPage from './UnauthorisedPage';
import { LinkProps } from 'react-router-dom';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { routes } from '../../types/generic/routes';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));

describe('UnauthorisedPage', () => {
    describe('Rendering', () => {
        it('renders unauthorised message', () => {
            render(<UnauthorisedPage />);
            expect(screen.getByText('Unauthorised access')).toBeInTheDocument();
        });

        it('renders a return home link', () => {
            render(<UnauthorisedPage />);
            expect(
                screen.getByRole('link', {
                    name: 'Return home',
                }),
            ).toBeInTheDocument();
        });

        it('pass accessibility checks', async () => {
            render(<UnauthorisedPage />);
            const results = await runAxeTest(document.body);

            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates user to home page when return home is clicked', async () => {
            render(<UnauthorisedPage />);
            const returnHomeLink = screen.getByRole('link', {
                name: 'Return home',
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
});
