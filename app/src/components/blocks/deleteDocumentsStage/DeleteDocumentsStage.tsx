import React, { Dispatch, SetStateAction, useState } from 'react';
import { FieldValues, useForm } from 'react-hook-form';
import { Button, Fieldset, Radios } from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import DeletionConfirmationStage from '../deletionConfirmationStage/DeletionConfirmationStage';
import deleteAllDocuments, { DeleteResponse } from '../../../helpers/requests/deleteAllDocuments';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import { DOCUMENT_TYPE } from '../../../types/pages/UploadDocumentsPage/types';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import SpinnerButton from '../../generic/spinnerButton/SpinnerButton';
import ServiceError from '../../layout/serviceErrorBox/ServiceErrorBox';
import { SUBMISSION_STATE } from '../../../types/pages/documentSearchResultsPage/types';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { AxiosError } from 'axios';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router-dom';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import usePatient from '../../../helpers/hooks/usePatient';

export type Props = {
    docType: DOCUMENT_TYPE;
    numberOfFiles: number;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    setIsDeletingDocuments?: Dispatch<SetStateAction<boolean>>;
    setDownloadStage?: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
};

enum DELETE_DOCUMENTS_OPTION {
    YES = 'yes',
    NO = 'no',
}

function DeleteDocumentsStage({
    docType,
    numberOfFiles,
    setStage,
    setIsDeletingDocuments,
    setDownloadStage,
}: Props) {
    const patientDetails = usePatient();
    const role = useRole();
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
        if (role === REPOSITORY_ROLE.GP_ADMIN && setStage) {
            setStage(LG_RECORD_STAGE.RECORD);
        } else if (role === REPOSITORY_ROLE.PCSE && setIsDeletingDocuments) {
            setIsDeletingDocuments(false);
        }
    };

    const submit = async (fieldValues: FieldValues) => {
        const allowedRoles = [REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.PCSE];
        if (role && allowedRoles.includes(role)) {
            if (fieldValues.deleteDocs === DELETE_DOCUMENTS_OPTION.YES) {
                await handleYesOption();
            } else if (fieldValues.deleteDocs === DELETE_DOCUMENTS_OPTION.NO) {
                handleNoOption();
            }
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
                            data-testid="yes-radio-btn"
                            defaultChecked
                        >
                            Yes
                        </Radios.Radio>
                        <Radios.Radio
                            value={DELETE_DOCUMENTS_OPTION.NO}
                            inputRef={deleteDocsRef}
                            {...radioProps}
                            id="no-radio-button"
                            data-testid="no-radio-btn"
                        >
                            No
                        </Radios.Radio>
                    </Radios>
                </Fieldset>
                {deletionStage === SUBMISSION_STATE.PENDING ? (
                    <SpinnerButton id="delete-docs-spinner" status="Deleting..." disabled={true} />
                ) : (
                    <Button type="submit" id="delete-submit-button" data-testid="delete-submit-btn">
                        Continue
                    </Button>
                )}
            </form>
        </>
    ) : (
        <DeletionConfirmationStage
            numberOfFiles={numberOfFiles}
            setStage={setStage}
            setDownloadStage={setDownloadStage}
        />
    );
}
export default DeleteDocumentsStage;
