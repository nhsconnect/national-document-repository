import React, { useEffect } from 'react';

type Props = { fileUrl: String };

const PdfViewer = ({ fileUrl }: Props) => {
    const options = {
        height: '400px',
        page: '2',
        pdfOpenParams: {
            view: 'FitV',
            pagemode: 'thumbs',
            search: 'lorem ipsum',
        },
    };
    useEffect(() => {
        const pdfObject = require('pdfobject');
        pdfObject.embed(fileUrl, '#pdf-viewer', options);
    }, []);

    return <div id="pdf-viewer"></div>;
};

export default PdfViewer;
