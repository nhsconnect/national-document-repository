import { render, screen } from '@testing-library/react';
import NotFoundPage from './NotFoundPage';
import { LinkProps } from 'react-router-dom';
import UploadDocumentsPage from '../uploadDocumentsPage/UploadDocumentsPage';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));
describe('NotFoundPage', () => {
    it('renders unauthorised message', () => {
        render(<NotFoundPage />);
        expect(screen.getByText('Page not found')).toBeInTheDocument();
    });

    it('pass accessibility checks', async () => {
        render(<NotFoundPage />);
        const results = await runAxeTest(document.body);

        expect(results).toHaveNoViolations();
    });
});
