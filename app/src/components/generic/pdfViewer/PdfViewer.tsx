import React, { useEffect, useRef, useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import { DocumentCallback } from 'react-pdf/src/shared/types';
import { PDFPageProxy } from 'pdfjs-dist';
import axios from 'axios';

pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

type MatchFound = {
    pageNumber: number;
    excerpt: string;
    keywordStart: number;
};

type Props = {
    fileUrl: string;
    searchTerm: string;
    updateSearchResultsCount: React.Dispatch<React.SetStateAction<number>>;
};

const PdfViewer = ({ fileUrl, searchTerm, updateSearchResultsCount }: Props) => {
    const [url, setUrl] = useState('');
    const [numPages, setNumPages] = useState<number>(1);
    const [pageNumber, setPageNumber] = useState<number>(1);
    const [pdfText, setPdfText] = useState<string[]>([]);

    useEffect(() => {
        const fetchPdf = async () => {
            try {
                const response = await axios.get(fileUrl, { responseType: 'blob' });
                const blobUrl = URL.createObjectURL(response.data);
                setUrl(blobUrl);
            } catch (error) {
                console.error('Error fetching PDF:', error);
            }
        };

        (async () => {
            await fetchPdf();
        })();
    }, [fileUrl]);

    useEffect(() => {
        console.log(pdfText);
        if (searchTerm) {
            findMatches();
        }
    }, [searchTerm, updateSearchResultsCount]);

    const onDocumentLoadSuccess = (props: DocumentCallback): void => {
        setNumPages(props.numPages);
        const allPages = [];
        for (let i = 1; i <= numPages; i++) {
            allPages.push(props.getPage(i).then(extractTextFromPage));
        }
        Promise.all(allPages).then((allPageTextContent) => setPdfText(allPageTextContent));
    };

    const extractTextFromPage = async (page: PDFPageProxy): Promise<string> => {
        const textContent = await page.getTextContent();
        return textContent.items.map((item) => ('str' in item ? item.str : '')).join(' ');
    };

    const findMatches = () => {
        if (searchTerm) {
            let count = 0;
            pdfText.forEach((text) => {
                const matches = text.match(new RegExp(searchTerm, 'gi'));

                if (matches) {
                    count += matches.length;
                }
            });
            console.log(count, ' results found');
            updateSearchResultsCount(count);
        }
    };

    const highlightKeywords = ({ str }: { str: string }) => {
        return str.replace(new RegExp(searchTerm, 'gi'), (value) => {
            return `<mark>${value}</mark>`;
        });
    };

    const handlePageChange = (page: number) => {
        setPageNumber(page);
    };

    return (
        <div>
            <div id="pdf-viewer" data-testid="pdf-viewer">
                <div>
                    <button
                        onClick={() => handlePageChange(pageNumber > 1 ? pageNumber - 1 : 1)}
                        disabled={pageNumber === 1}
                    >
                        &#8592;
                    </button>
                    Page {pageNumber} of {numPages}
                    <button
                        onClick={() =>
                            handlePageChange(pageNumber < numPages ? pageNumber + 1 : numPages)
                        }
                        disabled={pageNumber === numPages}
                    >
                        &#8594;
                    </button>
                </div>
                <Document file={url} onLoadSuccess={onDocumentLoadSuccess}>
                    <Page
                        pageNumber={pageNumber}
                        renderAnnotationLayer={false}
                        customTextRenderer={highlightKeywords}
                        canvasBackground="white"
                        scale={1.4}
                    ></Page>
                </Document>
            </div>
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
