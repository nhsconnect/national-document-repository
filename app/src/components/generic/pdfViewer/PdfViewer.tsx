import React, { useEffect, useState } from 'react';

type Props = { fileUrl: string };

const PdfViewer = ({ fileUrl }: Props) => {
    const [delayedFileUrl, setDelayedFileUrl] = useState<string | null>(null);
    const [showFileUrl, setShowFileUrl] = useState<string | null>(fileUrl);

    useEffect(() => {
        if (!fileUrl) return;
        const timer = setTimeout(() => {
            setDelayedFileUrl(fileUrl);
            setShowFileUrl(null);
        }, 180000);

        return () => clearTimeout(timer);
    }, [fileUrl]);

    if (!delayedFileUrl) {
        return (
            <div>
                <p>{showFileUrl}</p>
            </div>
        );
    }

    return (
        <div>
            <iframe
                id="pdf-viewer"
                data-testid="pdf-viewer"
                tabIndex={0}
                src={`/pdfjs/build/generic/web/viewer.html?file=${encodeURIComponent(fileUrl)}`}
                title="Embedded PDF Viewer"
                aria-label="PDF Viewer"
            />
        </div>
    );
};

export default PdfViewer;
