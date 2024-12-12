/*

import React, { useEffect, useRef, useState } from 'react';
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist';

// Set the worker path
GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

type Props = {
    fileUrl: string;
};

const PdfJs: React.FC<Props> = ({ fileUrl }) => {
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const [pageNumber, setPageNumber] = useState(1);
    const [numPages, setNumPages] = useState<number | null>(null);

    useEffect(() => {
        const renderPage = async (pageNum: number) => {
            const canvas = canvasRef.current;
            if (!canvas) return;

            const pdf = await getDocument(fileUrl).promise;
            setNumPages(pdf.numPages);

            const page = await pdf.getPage(pageNum);
            const viewport = page.getViewport({ scale: 1.5 });

            const context = canvas.getContext('2d');
            if (!context) return;

            canvas.width = viewport.width;
            canvas.height = viewport.height;

            const renderContext = {
                canvasContext: context,
                viewport,
            };

            await page.render(renderContext).promise;
        };

        renderPage(pageNumber).catch((err) => {
            console.error('Failed to render page:', err);
        });
    }, [fileUrl, pageNumber]);

    const goToPreviousPage = () => setPageNumber((prev) => Math.max(prev - 1, 1));
    const goToNextPage = () => setPageNumber((prev) => (numPages ? Math.min(prev + 1, numPages) : prev));

    return (
        <div id="pdfJs" >
            <div id="pdfJsButtons">
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
            <canvas ref={canvasRef} ></canvas>
        </div>
    );
};

export default PdfJs;

*/
