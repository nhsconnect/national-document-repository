import { useEffect } from 'react';
// @ts-ignore
import pdfObject from 'pdfobject';

type Props = { fileUrl: string };

const PdfViewer = ({ fileUrl }: Props) => {
    useEffect(() => {
        pdfObject.embed(fileUrl + '#toolbar', '#pdf-viewer');
    }, [fileUrl]);

    if (!fileUrl) return null;
    return (
        <div id="pdf-viewer" data-testid="pdf-viewer" tabIndex={0} style={{ height: 800 }}></div>
    );
};

export default PdfViewer;
