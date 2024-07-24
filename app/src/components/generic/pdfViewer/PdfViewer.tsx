import React, { useEffect, useState, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/TextLayer.css';
import { DocumentCallback } from 'react-pdf/src/shared/types';
import { PDFPageProxy } from 'pdfjs-dist';
import { Button } from 'nhsuk-react-components';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

type MatchFound = {
    pageNumber: number;
    excerpt: string;
    keywordStart: number;
};

type Props = { fileUrl: string; searchTerm: string };

const PdfViewer = ({ fileUrl, searchTerm }: Props) => {
    console.log(searchTerm);
    console.log(fileUrl);

    //pdfjs.GlobalWorkerOptions.workerSrc = "/pdf.worker.min.js";
    const [numPages, setNumPages] = useState<number>(1);
    const [pageNumber, setPageNumber] = useState<number>(1);

    function onDocumentLoadSuccess({ numPages }: { numPages: number }): void {
        setNumPages(numPages);
    }

    return (
        <div>
            <Document file={{ url: fileUrl }} onLoadSuccess={onDocumentLoadSuccess}>
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
