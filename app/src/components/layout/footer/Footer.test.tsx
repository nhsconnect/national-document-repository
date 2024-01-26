import { render, screen } from '@testing-library/react';
import Footer from './Footer';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../types/generic/routes';
const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    __esModule: true,
    useNavigate: () => mockedUseNavigate,
}));

describe('Footer', () => {
    describe('Rendering', () => {
        it('renders privacy policy link', () => {
            render(<Footer />);
            expect(screen.getByTestId('privacy-link')).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates to privacy policy when link is clicked', () => {
            render(<Footer />);
            expect(screen.getByTestId('privacy-link')).toBeInTheDocument();
            userEvent.click(screen.getByTestId('privacy-link'));
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.PRIVACY_POLICY);
        });
    });
});
