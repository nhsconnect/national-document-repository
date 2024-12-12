/*

import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';

// Point to the worker file
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

type Props = {
    fileUrl: string;
};

const ReactPdf: React.FC<Props> = ({ fileUrl }) => {
    const [numPages, setNumPages] = useState<number | null>(null);
    const [pageNumber, setPageNumber] = useState<number>(1);

    const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
        setNumPages(numPages);
    };

    const goToPreviousPage = () => setPageNumber((prevPage) => Math.max(prevPage - 1, 1));
    const goToNextPage = () => setPageNumber((prevPage) => (numPages ? Math.min(prevPage + 1, numPages) : prevPage));

    return (
        <div id="reactPdf">
            <div id="reactPdfButtons">
                <button onClick={goToPreviousPage} disabled={pageNumber === 1}>
                    Previous
                </button>
                <span>
                    Page {pageNumber} of {numPages}
                </span>
                <button onClick={goToNextPage} disabled={numPages !== null && pageNumber === numPages}>
                    Next
                </button>
            </div>
            <Document file={fileUrl} onLoadSuccess={onDocumentLoadSuccess}>
                <Page pageNumber={pageNumber} />
            </Document>
        </div>
    );
};

export default ReactPdf;

*/
