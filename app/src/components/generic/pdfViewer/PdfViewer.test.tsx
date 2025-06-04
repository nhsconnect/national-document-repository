import { render, screen } from '@testing-library/react';
import PdfViewer from './PdfViewer';
import { describe, expect, it } from 'vitest';

describe('PdfViewer', () => {
    it('renders an iframe element', () => {
        const fileUrl = 'https://test';

        render(<PdfViewer fileUrl={fileUrl} />);

        const pdfjsViewer = screen.getByTestId('pdf-viewer');

        expect(pdfjsViewer).toBeInTheDocument();
    });
});
