import { render, screen } from '@testing-library/react';
import PdfViewer from './PdfViewer';

describe('PdfViewer', () => {

    it('renders an iframe element', () => {

         const fileUrl = "https://test"

        render(<PdfViewer fileUrl={fileUrl} />);

        const iframeElement = screen.getByTitle('Embedded PDF Viewer') as HTMLIFrameElement;

        expect(iframeElement).toBeInTheDocument();
        expect(iframeElement.src).toContain("viewer.html");
        expect(iframeElement.src).toContain( encodeURIComponent(fileUrl) );

    });

});
