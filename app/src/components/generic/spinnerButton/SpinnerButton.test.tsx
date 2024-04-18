import { render, screen } from '@testing-library/react';
import SpinnerButton from './SpinnerButton';

describe('SpinnerButton', () => {
    it('displays status text for the spinner button', () => {
        const status = 'Loading...';

        render(<SpinnerButton id="test-spinner-button" status={status} />);

        expect(screen.getByRole('SpinnerButton', { name: status })).toBeInTheDocument();
        expect(screen.getByRole('status')).toBeInTheDocument();
    });
});
