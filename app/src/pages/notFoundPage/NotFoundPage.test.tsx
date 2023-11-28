import { render, screen } from '@testing-library/react';
import NotFoundPage from './NotFoundPage';
import { LinkProps } from 'react-router-dom';

jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));
describe('NotFoundPage', () => {
    it('renders unauthorised message', () => {
        render(<NotFoundPage />);
        expect(screen.getByText('Page not found')).toBeInTheDocument();
    });
});
