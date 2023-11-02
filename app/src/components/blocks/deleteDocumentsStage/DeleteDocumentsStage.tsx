import React, { Dispatch, SetStateAction, useState } from 'react';
import { FieldValues, useForm } from 'react-hook-form';
import { Button, Fieldset, Radios } from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import DeletionConfirmationStage from '../deletionConfirmationStage/DeletionConfirmationStage';
import deleteAllDocuments, { DeleteResponse } from '../../../helpers/requests/deleteAllDocuments';
import { useBaseAPIUrl } from '../../../providers/configProvider/ConfigProvider';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import { DOCUMENT_TYPE } from '../../../types/pages/UploadDocumentsPage/types';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import SpinnerButton from '../../generic/spinnerButton/SpinnerButton';
import ServiceError from '../../layout/serviceErrorBox/ServiceErrorBox';
import { SUBMISSION_STATE } from '../../../types/pages/documentSearchResultsPage/types';
import { USER_ROLE } from '../../../types/generic/roles';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { AxiosError } from 'axios';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router-dom';

export type Props = {
    docType: DOCUMENT_TYPE;
    numberOfFiles: number;
    patientDetails: PatientDetails;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    setIsDeletingDocuments?: Dispatch<SetStateAction<boolean>>;
    userType: USER_ROLE;
    setDownloadStage?: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
};

enum DELETE_DOCUMENTS_OPTION {
    YES = 'yes',
    NO = 'no',
}

function DeleteDocumentsStage({
    docType,
    numberOfFiles,
    patientDetails,
    setStage,
    setIsDeletingDocuments,
    userType,
    setDownloadStage,
}: Props) {
    const { register, handleSubmit } = useForm();
    const { ref: deleteDocsRef, ...radioProps } = register('deleteDocs');
    const [deletionStage, setDeletionStage] = useState(SUBMISSION_STATE.INITIAL);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const navigate = useNavigate();

    const nhsNumber: string = patientDetails?.nhsNumber || '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);

    const dob: String = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const patientInfo = (
        <>
            <p style={{ marginBottom: 5, fontWeight: '700' }}>
                {patientDetails?.givenName?.map((name: String) => `${name} `)}
                {patientDetails?.familyName}
            </p>
            <p style={{ fontSize: '16px', marginBottom: 5 }}>NHS number: {formattedNhsNumber}</p>
            <p style={{ fontSize: '16px' }}>Date of birth: {dob}</p>
        </>
    );

    const handleYesOption = async () => {
        setDeletionStage(SUBMISSION_STATE.PENDING);

        try {
            const response: DeleteResponse = await deleteAllDocuments({
                docType: docType,
                nhsNumber: nhsNumber,
                baseUrl,
                baseHeaders,
            });

            if (response.status === 200) {
                setDeletionStage(SUBMISSION_STATE.SUCCEEDED);

                if (setDownloadStage) {
                    setDownloadStage(DOWNLOAD_STAGE.FAILED);
                }
            }
        } catch (e) {
            const error = e as AxiosError;
            if (error.response?.status === 403) {
                navigate(routes.HOME);
            }
            setDeletionStage(SUBMISSION_STATE.FAILED);
        }
    };

    const handleNoOption = () => {
        if (userType === USER_ROLE.GP && setStage) {
            setStage(LG_RECORD_STAGE.RECORD);
        } else if (userType === USER_ROLE.PCSE && setIsDeletingDocuments) {
            setIsDeletingDocuments(false);
        }
    };

    const submit = async (fieldValues: FieldValues) => {
        if (fieldValues.deleteDocs === DELETE_DOCUMENTS_OPTION.YES) {
            await handleYesOption();
        } else if (fieldValues.deleteDocs === DELETE_DOCUMENTS_OPTION.NO) {
            handleNoOption();
        }
    };

    return deletionStage !== SUBMISSION_STATE.SUCCEEDED ? (
        <>
            {deletionStage === SUBMISSION_STATE.FAILED && <ServiceError />}
            <form onSubmit={handleSubmit(submit)}>
                <Fieldset>
                    <Fieldset.Legend isPageHeading>
                        Are you sure you want to permanently delete files for:
                    </Fieldset.Legend>
                    {patientInfo}
                    <Radios id="delete-docs">
                        <Radios.Radio
                            value={DELETE_DOCUMENTS_OPTION.YES}
                            inputRef={deleteDocsRef}
                            {...radioProps}
                            id="yes-radio-button"
                            defaultChecked
                        >
                            Yes
                        </Radios.Radio>
                        <Radios.Radio
                            value={DELETE_DOCUMENTS_OPTION.NO}
                            inputRef={deleteDocsRef}
                            {...radioProps}
                            id="no-radio-button"
                        >
                            No
                        </Radios.Radio>
                    </Radios>
                </Fieldset>
                {deletionStage === SUBMISSION_STATE.PENDING ? (
                    <SpinnerButton id="delete-docs-spinner" status="Deleting..." disabled={true} />
                ) : (
                    <Button type="submit" id="lg-delete-submit">
                        Continue
                    </Button>
                )}
            </form>
        </>
    ) : (
        <DeletionConfirmationStage
            numberOfFiles={numberOfFiles}
            patientDetails={patientDetails}
            setStage={setStage}
            userType={userType}
        />
    );
}
export default DeleteDocumentsStage;
