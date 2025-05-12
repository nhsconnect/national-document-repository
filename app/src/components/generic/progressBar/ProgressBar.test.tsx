import { render, screen } from '@testing-library/react';
import ProgressBar from './ProgressBar';
import { describe, expect, it } from 'vitest';

describe('ProgressBar', () => {
    it('displays status text for the progress bar', () => {
        const status = 'Loading...';

        render(<ProgressBar status={status} />);

        expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
        expect(screen.getByRole('status')).toBeInTheDocument();
    });
});
