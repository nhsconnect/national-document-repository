import React, { Dispatch, SetStateAction, useState } from 'react';
import { FieldValues, useForm } from 'react-hook-form';
import { Button, Fieldset, Radios } from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import DeletionConfirmationStage from '../deletionConfirmationStage/DeletionConfirmationStage';
import deleteAllDocuments from '../../../helpers/requests/deleteAllDocuments';
import { useBaseAPIUrl } from '../../../providers/configProvider/ConfigProvider';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import { DOCUMENT_TYPE } from '../../../types/pages/UploadDocumentsPage/types';
import { AxiosError } from 'axios';
import { routes } from '../../../types/generic/routes';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import SpinnerButton from '../../generic/spinnerButton/SpinnerButton';
import ServiceError from '../../layout/serviceErrorBox/ServiceErrorBox';
import { SUBMISSION_STATE } from '../../../types/pages/documentSearchResultsPage/types';
import { USER_ROLE } from '../../../types/generic/roles';

export type Props = {
    docType: DOCUMENT_TYPE;
    numberOfFiles: number;
    patientDetails: PatientDetails;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    setIsDeletingDocuments?: Dispatch<SetStateAction<boolean>>;
    userType: USER_ROLE;
    setDownloadStage?: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
    passNavigate: (navigateTo: string) => void;
};

function DeleteDocumentsStage({
    docType,
    numberOfFiles,
    patientDetails,
    setStage,
    setIsDeletingDocuments,
    userType,
    passNavigate,
    setDownloadStage,
}: Props) {
    const { register, handleSubmit } = useForm();
    const { ref: deleteDocsRef, ...radioProps } = register('deleteDocs');
    const [deletionStage, setDeletionStage] = useState(SUBMISSION_STATE.INITIAL);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const dob: String = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const nhsNumber: string =
        patientDetails?.nhsNumber.slice(0, 3) +
        ' ' +
        patientDetails?.nhsNumber.slice(3, 6) +
        ' ' +
        patientDetails?.nhsNumber.slice(6, 10);

    const patientInfo = (
        <>
            <p style={{ marginBottom: 5, fontWeight: '700' }}>
                {patientDetails?.givenName?.map((name: String) => `${name} `)}
                {patientDetails?.familyName}
            </p>
            <p style={{ fontSize: '16px', marginBottom: 5 }}>NHS number: {nhsNumber}</p>
            <p style={{ fontSize: '16px' }}>Date of birth: {dob}</p>
        </>
    );

    const submit = async (fieldValues: FieldValues) => {
        const patientNhsNumber: string = patientDetails?.nhsNumber || '';

        if (fieldValues.deleteDocs === 'yes') {
            setDeletionStage(SUBMISSION_STATE.PENDING);
            let response;
            try {
                if (docType === DOCUMENT_TYPE.LLOYD_GEORGE) {
                    response = await deleteAllDocuments({
                        docType,
                        nhsNumber: patientNhsNumber,
                        baseUrl,
                        baseHeaders,
                    });
                }
                if (docType === DOCUMENT_TYPE.ALL) {
                    response = await deleteAllDocuments({
                        docType: DOCUMENT_TYPE.ARF,
                        nhsNumber: patientNhsNumber,
                        baseUrl,
                        baseHeaders,
                    });
                    response = await deleteAllDocuments({
                        docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                        nhsNumber: patientNhsNumber,
                        baseUrl,
                        baseHeaders,
                    });
                }
                if (response?.status === 200) {
                    setDeletionStage(SUBMISSION_STATE.SUCCEEDED);
                    if (setDownloadStage) {
                        setDownloadStage(DOWNLOAD_STAGE.FAILED);
                    }
                }
            } catch (e) {
                setDeletionStage(SUBMISSION_STATE.FAILED);
                const error = e as AxiosError;
                if (error.response?.status === 403) {
                    passNavigate(routes.HOME);
                }
            }
        } else if (fieldValues.deleteDocs === 'no') {
            if (userType === USER_ROLE.GP) {
                if (setStage) {
                    setStage(LG_RECORD_STAGE.RECORD);
                }
            }
            if (userType === USER_ROLE.PCSE) {
                if (setIsDeletingDocuments) {
                    setIsDeletingDocuments(false);
                }
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
                            value="yes"
                            inputRef={deleteDocsRef}
                            {...radioProps}
                            id="yes-radio-button"
                            defaultChecked
                        >
                            Yes
                        </Radios.Radio>
                        <Radios.Radio
                            value="no"
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
            passNavigate={passNavigate}
        />
    );
}
export default DeleteDocumentsStage;
