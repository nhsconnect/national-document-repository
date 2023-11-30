import React, { useEffect, useRef, useState } from 'react';
import { DOWNLOAD_STAGE } from '../../types/generic/downloadStage';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import DeleteDocumentsStage from '../../components/blocks/deleteDocumentsStage/DeleteDocumentsStage';
import { getFormattedDatetime } from '../../helpers/utils/formatDatetime';
import getLloydGeorgeRecord from '../../helpers/requests/getLloydGeorgeRecord';
import LloydGeorgeRecordStage from '../../components/blocks/lloydGeorgeRecordStage/LloydGeorgeRecordStage';
import LloydGeorgeDownloadAllStage from '../../components/blocks/lloydGeorgeDownloadAllStage/LloydGeorgeDownloadAllStage';
import { DOCUMENT_TYPE } from '../../types/pages/UploadDocumentsPage/types';
import { LG_RECORD_STAGE } from '../../types/blocks/lloydGeorgeStages';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import usePatient from '../../helpers/hooks/usePatient';

function LloydGeorgeRecordPage() {
    const patientDetails = usePatient();
    const [downloadStage, setDownloadStage] = useState(DOWNLOAD_STAGE.INITIAL);
    const [numberOfFiles, setNumberOfFiles] = useState(0);
    const [totalFileSizeInByte, setTotalFileSizeInByte] = useState(0);
    const [lastUpdated, setLastUpdated] = useState('');
    const [lloydGeorgeUrl, setLloydGeorgeUrl] = useState('');
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const mounted = useRef(false);
    const [stage, setStage] = useState(LG_RECORD_STAGE.RECORD);

    useEffect(() => {
        const onPageLoad = async () => {
            setDownloadStage(DOWNLOAD_STAGE.PENDING);
            const nhsNumber: string = patientDetails?.nhsNumber || '';
            try {
                const { number_of_files, total_file_size_in_byte, last_updated, presign_url } =
                    await getLloydGeorgeRecord({
                        nhsNumber,
                        baseUrl,
                        baseHeaders,
                    });
                if (presign_url?.startsWith('https://')) {
                    setNumberOfFiles(number_of_files);
                    setLastUpdated(getFormattedDatetime(new Date(last_updated)));
                    setLloydGeorgeUrl(presign_url);
                    setDownloadStage(DOWNLOAD_STAGE.SUCCEEDED);
                    setTotalFileSizeInByte(total_file_size_in_byte);
                }
                setDownloadStage(DOWNLOAD_STAGE.SUCCEEDED);
            } catch (e) {
                setDownloadStage(DOWNLOAD_STAGE.FAILED);
            }
        };
        if (!mounted.current) {
            mounted.current = true;
            void onPageLoad();
        }
    }, [
        patientDetails,
        baseUrl,
        baseHeaders,
        setDownloadStage,
        setLloydGeorgeUrl,
        setLastUpdated,
        setNumberOfFiles,
        setTotalFileSizeInByte,
    ]);

    switch (stage) {
        case LG_RECORD_STAGE.RECORD:
            return (
                <LloydGeorgeRecordStage
                    numberOfFiles={numberOfFiles}
                    totalFileSizeInByte={totalFileSizeInByte}
                    lastUpdated={lastUpdated}
                    lloydGeorgeUrl={lloydGeorgeUrl}
                    downloadStage={downloadStage}
                    setStage={setStage}
                    stage={stage}
                />
            );
        case LG_RECORD_STAGE.DOWNLOAD_ALL:
            return (
                <LloydGeorgeDownloadAllStage numberOfFiles={numberOfFiles} setStage={setStage} />
            );
        case LG_RECORD_STAGE.DELETE_ALL:
            return (
                <DeleteDocumentsStage
                    docType={DOCUMENT_TYPE.LLOYD_GEORGE}
                    numberOfFiles={numberOfFiles}
                    setStage={setStage}
                    setDownloadStage={setDownloadStage}
                />
            );
        default:
            return <div></div>;
    }
}

export default LloydGeorgeRecordPage;
