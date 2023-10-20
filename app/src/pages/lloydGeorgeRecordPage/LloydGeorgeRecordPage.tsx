import React, { useEffect, useRef, useState } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import { useNavigate } from 'react-router';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import { DOWNLOAD_STAGE } from '../../types/generic/downloadStage';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import { getFormattedDatetime } from '../../helpers/utils/formatDatetime';
import getLloydGeorgeRecord from '../../helpers/requests/getLloydGeorgeRecord';
import LloydGeorgeRecordStage from '../../components/blocks/lloydGeorgeRecordStage/LloydGeorgeRecordStage';
import LloydGeorgeDownloadAllStage from '../../components/blocks/lloydGeorgeDownloadAllStage/LloydGeorgeDownloadAllStage';

export enum LG_RECORD_STAGE {
    RECORD = 0,
    DOWNLOAD_ALL = 1,
    SEE_ALL = 2,
    DELETE_ANY = 3,
    DELETE_ONE = 4,
}
function LloydGeorgeRecordPage() {
    const [patientDetails] = usePatientDetailsContext();
    const [downloadStage, setDownloadStage] = useState(DOWNLOAD_STAGE.INITIAL);
    const [numberOfFiles, setNumberOfFiles] = useState(0);
    const [totalFileSizeInByte, setTotalFileSizeInByte] = useState(0);
    const [lastUpdated, setLastUpdated] = useState('');
    const [lloydGeorgeUrl, setLloydGeorgeUrl] = useState('');
    const navigate = useNavigate();
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
        navigate,
        setDownloadStage,
        setLloydGeorgeUrl,
        setLastUpdated,
        setNumberOfFiles,
        setTotalFileSizeInByte,
    ]);

    switch (stage) {
        case LG_RECORD_STAGE.RECORD:
            return (
                patientDetails && (
                    <LloydGeorgeRecordStage
                        numberOfFiles={numberOfFiles}
                        totalFileSizeInByte={totalFileSizeInByte}
                        lastUpdated={lastUpdated}
                        lloydGeorgeUrl={lloydGeorgeUrl}
                        patientDetails={patientDetails}
                        downloadStage={downloadStage}
                        setStage={setStage}
                        stage={stage}
                    />
                )
            );
        case LG_RECORD_STAGE.DOWNLOAD_ALL:
            return (
                patientDetails && (
                    <LloydGeorgeDownloadAllStage
                        numberOfFiles={numberOfFiles}
                        setStage={setStage}
                        patientDetails={patientDetails}
                    />
                )
            );
        default:
            return <div />;
    }
}

export default LloydGeorgeRecordPage;
