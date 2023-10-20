import { render, screen } from '@testing-library/react';
import PdfViewer from './PdfViewer';

describe('PdfViewer', () => {
    it('renders an embed element', () => {
        render(<PdfViewer fileUrl="https://test" />);

        expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
    });
});
