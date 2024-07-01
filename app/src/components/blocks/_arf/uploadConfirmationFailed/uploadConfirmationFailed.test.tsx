import UploadConfirmationFailed from './uploadConfirmationFailed';
import { render, screen } from '@testing-library/react';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';

describe('UploadConfirmationFailed', () => {
    it('renders the page', () => {
        render(<UploadConfirmationFailed />);

        expect(
            screen.getByRole('heading', { name: "We couldn't confirm the upload" }),
        ).toBeInTheDocument();
    });

    it('pass accessibility checks at page entry point', async () => {
        render(<UploadConfirmationFailed />);

        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });
});
