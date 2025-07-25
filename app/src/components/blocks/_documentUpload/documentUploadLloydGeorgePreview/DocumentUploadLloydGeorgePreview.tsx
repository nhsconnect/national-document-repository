import PDFMerger from 'pdf-merger-js/browser';
import { UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import PdfViewer from '../../../generic/pdfViewer/PdfViewer';
import Spinner from '../../../generic/spinner/Spinner';

type Props = {
    documents: UploadDocument[];
    previewLoading: boolean;
    setPreviewLoading: Dispatch<SetStateAction<boolean>>;
    setMergedPdfBlob: Dispatch<SetStateAction<Blob | undefined>>;
};

const DocumentUploadLloydGeorgePreview = ({
    documents,
    previewLoading,
    setPreviewLoading,
    setMergedPdfBlob,
}: Props) => {
    const [mergedPdfUrl, setMergedPdfUrl] = useState('');

    const runningRef = useRef(false);
    useEffect(() => {
        if (!documents || runningRef.current) {
            return;
        }

        runningRef.current = true;

        const render = async () => {
            const merger = new PDFMerger();

            for (const doc of documents) {
                let attempts = 0;

                do {
                    try {
                        await merger.add(doc.file);

                        attempts = 3;
                    } catch (err) {
                        attempts += 1;

                        if (attempts === 3) {
                            throw err;
                        }
                    }
                } while (attempts < 3);
            }

            await merger.setMetadata({
                producer: 'pdf-merger-js based script',
            });

            const blob = await merger.saveAsBlob();
            setMergedPdfBlob(blob);

            const url = URL.createObjectURL(blob);

            runningRef.current = false;
            setPreviewLoading(false);
            return setMergedPdfUrl(url);
        };

        setPreviewLoading(true);
        render().catch((err) => {
            setPreviewLoading(false);
            runningRef.current = false;
            throw err;
        });
    }, [JSON.stringify(documents)]);

    const loaded = () => {};

    return (
        <>
            {previewLoading && <Spinner status="Loading preview..."></Spinner>}
            {documents && mergedPdfUrl && !previewLoading && (
                <PdfViewer
                    customClasses={['upload-preview']}
                    fileUrl={mergedPdfUrl}
                    onLoaded={loaded}
                />
            )}
        </>
    );
};

export default DocumentUploadLloydGeorgePreview;
