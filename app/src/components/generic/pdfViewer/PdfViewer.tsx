import React, { useEffect, useState, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/TextLayer.css';
import { DocumentCallback } from 'react-pdf/src/shared/types';
import { PDFPageProxy } from 'pdfjs-dist';
import { Button } from 'nhsuk-react-components';
import axios from 'axios';

//pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

type MatchFound = {
    pageNumber: number;
    excerpt: string;
    keywordStart: number;
};

type Props = { fileUrl: string; searchTerm: string };

const PdfViewer = ({ fileUrl, searchTerm }: Props) => {
    console.log(searchTerm);
    console.log(fileUrl);

    const [url, setUrl] = useState('');
    const [blob, setBlob] = useState<Blob | null>(null);
    const [base64, setBase64] = useState<string | null>(null);
    const [numPages, setNumPages] = useState<number>(1);
    const [pageNumber, setPageNumber] = useState<number>(1);

    useEffect(() => {
        const fetchPdf = async () => {
            try {
                //const response = await fetch(fileUrl);
                //Blob
                const response = await axios.get(fileUrl, { responseType: 'blob' });
                console.log(response, '<-- response');
                const blobUrl = URL.createObjectURL(response.data);
                console.log(blobUrl, '<--- blob url');
                setUrl(blobUrl);

                //b64
                // const response = await fetch(fileUrl);
                // const arrayBuffer = await response.arrayBuffer();
                // const base64String = arrayBufferToBase64(arrayBuffer);
                // setBase64(base64String);
            } catch (error) {
                console.error('Error fetching PDF:', error);
            }
        };

        fetchPdf();
    }, [fileUrl]);

    const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    };
    function onDocumentLoadSuccess({ numPages }: { numPages: number }): void {
        setNumPages(numPages);
    }

    return (
        <div>
            <Document file={fileUrl} onLoadSuccess={onDocumentLoadSuccess}>
                <Page pageNumber={pageNumber} />
            </Document>
            <p>
                Page {pageNumber} of {numPages}
            </p>
        </div>
    );

    // const [pageNumber, setPageNumber] = useState<number>(1);
    // const [keyword, setKeyword] = useState<string>("");
    // const [pdfText, setPdfText] = useState<string[]>([]);
    // const [searchResult, setSearchResult] = useState<MatchFound[]>([]);
    // useEffect(() => {
    //     const pdfObject = require('pdfobject');
    //     pdfObject.embed(fileUrl + '#toolbar=0', '#pdf-viewer');
    // }, [fileUrl]);
    //
    // const onDocumentLoadSuccess = (props: DocumentCallback): void => {
    //     setTotalNumOfPages(props.numPages);
    //     const allPages = [];
    //     for (let i = 1; i <= props.numPages; i++) {
    //       allPages.push(props.getPage(i).then(extractTextFromPage));
    //     }
    //     Promise.all(allPages).then((allPageTextContent) =>
    //       setPdfText(allPageTextContent),
    //     );
    //   };
    //
    // const extractTextFromPage = async (page: PDFPageProxy): Promise<string> => {
    //     const textContent = await page.getTextContent();
    //     const extractedText = textContent.items
    //       .map((item) => ("str" in item ? item.str : ""))
    //       .join(" ");
    //     return extractedText;
    //   };
    //
    // const highlightKeywords = ({ str }: { str: string }) => {
    //     return str.replace(
    //       new RegExp(keyword, "gi"),
    //       (value) => `<mark>${value}</mark>`,
    //     );
    // };
    //
    // const PageSelect = () => {
    //     const prevPage = () => {
    //       setPageNumber((curr) => Math.max(curr - 1, 1));
    //     };
    //     const nextPage = () => {
    //       setPageNumber((curr) => Math.min(curr + 1, totalNumOfPages));
    //     };
    //     return (
    //       <div style={{ display: "flex", justifyContent: "space-evenly" }}>
    //         <Button onClick={prevPage} disabled={pageNumber === 1}>
    //           Previous page
    //         </Button>
    //         <Button onClick={nextPage} disabled={pageNumber === totalNumOfPages}>
    //           Next page
    //         </Button>
    //       </div>
    //     );
    //   };
    //
    // const pager = (
    // <Page
    //       pageNumber={pageNumber}
    //       renderAnnotationLayer={false}
    //       customTextRenderer={highlightKeywords}
    //       canvasBackground="white"
    //       scale={1.4}
    //     ></Page>
    //   );
    //
    // return (
    //     <div>
    //         <div id="pdf-viewer" data-testid="pdf-viewer" tabIndex={0} style={{ height: 600 }}></div>
    //         <Document
    //             className="document"
    //             file={fileUrl}
    //             onLoadSuccess={onDocumentLoadSuccess}
    //           >
    //             {pager}
    //             <PageSelect />
    //           </Document>
    //     </div>
    // );
};

export default PdfViewer;
