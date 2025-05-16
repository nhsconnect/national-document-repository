import { render, screen } from '@testing-library/react';
import NotFoundPage from './NotFoundPage';
import { LinkProps } from 'react-router-dom';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { describe, expect, it, vi } from 'vitest';

vi.mock('react-router-dom', () => ({
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
