import React, { useState } from 'react';
import { UPLOAD_STAGE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import uploadDocument from '../../helpers/requests/uploadDocument';
import SelectStage from '../../components/blocks/_arf/selectStage/SelectStage';
import UploadingStage from '../../components/blocks/_arf/uploadingStage/UploadingStage';
import CompleteStage from '../../components/blocks/_arf/completeStage/CompleteStage';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import usePatient from '../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';

type Props = {};

function UploadDocumentsPage(props: Props) {
    const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const patientDetails = usePatient();

    const uploadDocuments = async () => {
        if (patientDetails) {
            setStage(UPLOAD_STAGE.Uploading);
            await uploadDocument({
                nhsNumber: patientDetails.nhsNumber,
                setDocuments,
                documents,
                baseUrl,
                baseHeaders,
            });
            setStage(UPLOAD_STAGE.Complete);
        }
    };

    if (stage === UPLOAD_STAGE.Selecting && patientDetails) {
        return <SelectStage uploadDocuments={uploadDocuments} setDocuments={setDocuments} />;
    } else if (stage === UPLOAD_STAGE.Uploading && patientDetails) {
        return <UploadingStage documents={documents} />;
    } else if (stage === UPLOAD_STAGE.Complete && patientDetails) {
        return <CompleteStage documents={documents} />;
    }
    return null;
}

export default UploadDocumentsPage;
