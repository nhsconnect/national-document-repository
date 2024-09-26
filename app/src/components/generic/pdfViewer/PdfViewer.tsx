import React, { useEffect } from 'react';

type Props = { fileUrl: String };

const PdfViewer = ({ fileUrl }: Props) => {
    useEffect(() => {
        const pdfObject = require('pdfobject');
        pdfObject.embed(fileUrl + '#toolbar=0', '#pdf-viewer');
    }, [fileUrl]);

    if (!fileUrl) return null;
    return (
        <div id="pdf-viewer" data-testid="pdf-viewer" tabIndex={0} style={{ height: 600 }}></div>
    );
};

export default PdfViewer;
