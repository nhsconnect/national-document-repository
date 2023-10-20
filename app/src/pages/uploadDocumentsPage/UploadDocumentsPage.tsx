import React, { useState } from 'react';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UPLOAD_STAGE,
    UploadDocument,
} from '../../types/pages/UploadDocumentsPage/types';
import uploadDocument from '../../helpers/requests/uploadDocument';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import SelectStage from '../../components/blocks/selectStage/SelectStage';
import UploadingStage from '../../components/blocks/uploadingStage/UploadingStage';
import CompleteStage from '../../components/blocks/completeStage/CompleteStage';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';

type Props = {};

function UploadDocumentsPage(props: Props) {
    const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const [patientDetails] = usePatientDetailsContext();

    const setDocumentState = (id: string, state: DOCUMENT_UPLOAD_STATE, progress?: number) => {
        setDocuments((prevDocuments) => {
            const updatedDocuments = prevDocuments.map((document) => {
                if (document.id === id) {
                    progress = progress ?? document.progress;
                    return { ...document, state, progress };
                }
                return document;
            });
            return updatedDocuments;
        });
    };

    const uploadDocuments = async () => {
        if (patientDetails) {
            setStage(UPLOAD_STAGE.Uploading);
            await uploadDocument({
                nhsNumber: patientDetails.nhsNumber,
                docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                setDocumentState,
                documents,
                baseUrl,
                baseHeaders,
            });
            setStage(UPLOAD_STAGE.Complete);
        }
    };

    if (stage === UPLOAD_STAGE.Selecting && patientDetails) {
        return (
            <SelectStage
                patientDetails={patientDetails}
                uploadDocuments={uploadDocuments}
                setDocuments={setDocuments}
            />
        );
    } else if (stage === UPLOAD_STAGE.Uploading && patientDetails) {
        return <UploadingStage patientDetails={patientDetails} documents={documents} />;
    } else if (stage === UPLOAD_STAGE.Complete && patientDetails) {
        return <CompleteStage patientDetails={patientDetails} documents={documents} />;
    }
    return null;
}

export default UploadDocumentsPage;
