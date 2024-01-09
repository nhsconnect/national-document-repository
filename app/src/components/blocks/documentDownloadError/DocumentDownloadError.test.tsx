import {render, screen } from '@testing-library/react';
import DocumentDownloadError from "./DocumentDownloadError";

describe('DocumentDownloadError', () => {
    it( 'Render a relevant error box', async () => {
        render(<DocumentDownloadError/>);
        expect(
            await screen.findByText('An error has occurred while preparing your download'),
        ).toBeInTheDocument();
    })
});
