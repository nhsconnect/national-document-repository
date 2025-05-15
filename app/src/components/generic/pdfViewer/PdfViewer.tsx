type Props = { fileUrl: string };

const PdfViewer = ({ fileUrl }: Props) => {
    if (!fileUrl) return null;

    return (
        <pdfjs-viewer-element
            id="pdf-viewer"
            data-testid="pdf-viewer"
            src={fileUrl}
            title="Embedded PDF Viewer"
            viewer-path="/pdfjs"
            viewer-extra-styles-urls="['/pdf-viewer.css']"
        ></pdfjs-viewer-element>
    );
};

export default PdfViewer;
