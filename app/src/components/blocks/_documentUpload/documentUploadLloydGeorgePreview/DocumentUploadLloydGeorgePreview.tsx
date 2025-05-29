import PDFMerger from 'pdf-merger-js/browser';
import { UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import { useEffect, useState } from 'react';
import PdfViewer from '../../../generic/pdfViewer/PdfViewer';

type Props = {
    documents: UploadDocument[];
};

const DocumentUploadLloydGeorgePreview = ({ documents }: Props) => {
    const [mergedPdfUrl, setMergedPdfUrl] = useState('');
    useEffect(() => {
        if (!documents) {
            return;
        }

        const render = async () => {
            const merger = new PDFMerger();

            for (const doc of documents) {
                await merger.add(doc.file);
            }

            await merger.setMetadata({
                producer: 'pdf-merger-js based script',
            });

            const blob = await merger.saveAsBlob();
            const url = URL.createObjectURL(blob);

            return setMergedPdfUrl(url);
        };

        render().catch((err) => {
            throw err;
        });
    }, [documents, setMergedPdfUrl]);

    return (
        <>
            {documents && mergedPdfUrl && (
                <PdfViewer customClasses={['upload-preview']} fileUrl={mergedPdfUrl} />
            )}
        </>
    );
};

export default DocumentUploadLloydGeorgePreview;
