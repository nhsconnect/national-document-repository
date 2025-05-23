import { render, screen } from '@testing-library/react';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import UploadFailedStage from './uploadFailedStage';
import { describe, expect, it } from 'vitest';

describe('UploadFailedStage', () => {
    it('renders the page', () => {
        render(<UploadFailedStage />);

        expect(
            screen.getByRole('heading', { name: 'All files failed to upload' }),
        ).toBeInTheDocument();
    });

    it('pass accessibility checks at page entry point', async () => {
        render(<UploadFailedStage />);

        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });
});
