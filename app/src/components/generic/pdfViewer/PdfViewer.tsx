import { useEffect, useRef } from 'react';

type Props = {
    fileUrl: string;
    customClasses?: string[];
    onLoaded?: () => void;
};

const PdfViewer = ({ fileUrl, customClasses, onLoaded }: Props) => {
    let loaded = false;

    useEffect(() => {
        const test = async () => {
            while (!document.querySelector('pdfjs-viewer-element')) {}

            if (onLoaded && !loaded) {
                loaded = true;
                onLoaded();
            }
        };

        test();
    }, []);

    return (
        <pdfjs-viewer-element
            id="pdf-viewer"
            data-testid="pdf-viewer"
            src={fileUrl}
            title="Embedded PDF Viewer"
            viewer-path="/pdfjs"
            viewer-extra-styles-urls="['/pdf-viewer.css']"
            className={customClasses?.join(' ')}
        ></pdfjs-viewer-element>
    );
};

export default PdfViewer;
