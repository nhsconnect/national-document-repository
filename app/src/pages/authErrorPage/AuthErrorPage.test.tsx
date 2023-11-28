import { render, screen } from '@testing-library/react';
import AuthErrorPage from './AuthErrorPage';
import { LinkProps } from 'react-router-dom';

jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));
describe('AuthErrorPage', () => {
    it('renders unauthorised message', () => {
        render(<AuthErrorPage />);
        expect(screen.getByText('You have been logged out')).toBeInTheDocument();
    });
});
