import React from 'react';

type Props = { fileUrl: string };

const PdfViewer = ({ fileUrl }: Props) => {
    if (!fileUrl) return null;
    return (
        <div>
            <iframe
                id="pdf-viewer"
                data-testid="pdf-viewer"
                tabIndex={0}
                src={`/pdfjs/build/generic/web/viewer.html?file=${encodeURIComponent(fileUrl)}`}
                title="Embedded PDF Viewer"
                aria-label="PDF Viewer"
                sandbox="allow-scripts allow-same-origin allow-modals"
            />
        </div>
    );
};

export default PdfViewer;
