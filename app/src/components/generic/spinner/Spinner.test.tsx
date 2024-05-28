import { render, screen } from '@testing-library/react';
import Spinner from './Spinner';
import { runAxeTest } from '../../../helpers/test/axeTestHelper';

describe('Spinner', () => {
    it('displays status text for the spinner', () => {
        const status = 'Loading...';

        render(<Spinner status={status} />);

        expect(screen.getByText(status)).toBeInTheDocument();
        expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('pass accessibility checks', async () => {
        render(<Spinner status={'Loading...'} />);
        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });
});
