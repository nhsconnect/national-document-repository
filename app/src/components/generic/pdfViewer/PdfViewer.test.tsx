import { render, screen } from '@testing-library/react';
import PdfViewer from './PdfViewer';

describe('PdfViewer', () => {
    it('renders an embed element', () => {
        render(<PdfViewer fileUrl="https://test" />);

        const embedElement = screen.getByTitle('Embedded PDF') as HTMLEmbedElement;
        expect(embedElement).toBeInTheDocument();
        expect(embedElement.src).toMatch(/#toolbar$/);
    });
});
