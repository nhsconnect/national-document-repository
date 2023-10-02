import React, { useEffect } from 'react';

type Props = { fileUrl: String };

const PdfViewer = ({ fileUrl }: Props) => {
    useEffect(() => {
        const pdfObject = require('pdfobject');
        pdfObject.embed(fileUrl + '#toolbar=0', '#pdf-viewer');
    }, [fileUrl]);

    return <div id="pdf-viewer" style={{ height: 600 }}></div>;
};

export default PdfViewer;
