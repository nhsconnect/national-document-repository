import { render, screen } from '@testing-library/react';
import AuthErrorPage from './AuthErrorPage';
import { LinkProps } from 'react-router-dom';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

jest.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));
describe('AuthErrorPage', () => {
    it('renders unauthorised message', () => {
        render(<AuthErrorPage />);
        expect(screen.getByText('You have been logged out')).toBeInTheDocument();
    });

    it('pass accessibility checks', async () => {
        render(<AuthErrorPage />);
        const results = await runAxeTest(document.body);

        expect(results).toHaveNoViolations();
    });
});
