import { render, screen } from '@testing-library/react';
import SpinnerButton from './SpinnerButton';
import { runAxeTest } from '../../../helpers/test/axeTestHelper';

describe('SpinnerButton', () => {
    it('displays status text for the spinner button', () => {
        const status = 'Loading...';

        render(<SpinnerButton id="test-spinner-button" status={status} />);

        expect(screen.getByRole('button', { name: status })).toBeInTheDocument();
        expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('pass accessibility checks', async () => {
        render(<SpinnerButton id="test-spinner-button" status={'Loading...'} />);
        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });
});
