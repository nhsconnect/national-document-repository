import PDFMerger from 'pdf-merger-js/browser';
import { UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import { Dispatch, SetStateAction, useEffect, useState } from 'react';
import PdfViewer from '../../../generic/pdfViewer/PdfViewer';
import moment from 'moment';
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

    let running = false;
    let start = moment().unix();
    useEffect(() => {
        if (!documents || running) {
            return;
        }

        running = true;

        const render = async () => {
            start = moment().unix();
            console.log(`start merge @ ${start}`);
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

            running = false;
            setPreviewLoading(false);
            return setMergedPdfUrl(url);
        };

        setPreviewLoading(true);
        render().catch((err) => {
            setPreviewLoading(false);
            running = false;
            throw err;
        });
    }, [JSON.stringify(documents)]);

    const loaded = () => {
        const end = moment().unix();
        console.log(`end merge @ ${end}`);
        console.log(`merge duration: ${end - start} seconds`);
    };

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
