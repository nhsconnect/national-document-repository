import React, { Dispatch, SetStateAction, useState } from 'react';
import { FieldValues, useForm } from 'react-hook-form';
import { BackLink, Button, Fieldset, Radios } from 'nhsuk-react-components';
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
import { routeChildren, routes } from '../../../types/generic/routes';
import { Outlet, Route, Routes, useNavigate } from 'react-router-dom';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import usePatient from '../../../helpers/hooks/usePatient';
import { errorToParams } from '../../../helpers/utils/errorToParams';
import { isMock } from '../../../helpers/utils/isLocal';
import useConfig from '../../../helpers/hooks/useConfig';
import useTitle from '../../../helpers/hooks/useTitle';
import ErrorBox from '../../layout/errorBox/ErrorBox';

export type Props = {
    docType: DOCUMENT_TYPE;
    numberOfFiles: number;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    setIsDeletingDocuments?: Dispatch<boolean>;
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
    const config = useConfig();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const [showNoOptionSelectedMessage, setShowNoOptionSelectedMessage] = useState<boolean>(false);
    const noOptionSelectedError =
        'Select whether you want to permanently delete these patient files';
    const dob: string = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const patientInfo = (
        <>
            <p style={{ marginBottom: 5, fontWeight: '700' }}>
                {patientDetails?.givenName?.map((name: String) => `${name} `)}
                {patientDetails?.familyName}
            </p>
            <p style={{ fontSize: '1rem', marginBottom: 5 }}>NHS number: {formattedNhsNumber}</p>
            <p style={{ fontSize: '1rem' }}>Date of birth: {dob}</p>
        </>
    );
    const userIsGP = role === REPOSITORY_ROLE.GP_ADMIN || role === REPOSITORY_ROLE.GP_CLINICAL;

    const handleYesOption = async () => {
        const onSuccess = () => {
            setDeletionStage(SUBMISSION_STATE.SUCCEEDED);
            if (setDownloadStage) {
                setDownloadStage(DOWNLOAD_STAGE.FAILED);
            }
        };
        try {
            const response: DeleteResponse = await deleteAllDocuments({
                docType: docType,
                nhsNumber: nhsNumber,
                baseUrl,
                baseHeaders,
            });

            if (response.status === 200) {
                onSuccess();
                if (userIsGP) {
                    navigate(routeChildren.LLOYD_GEORGE_DELETE_COMPLETE);
                } else {
                    navigate(routeChildren.ARF_DELETE_COMPLETE);
                }
            }
        } catch (e) {
            const error = e as AxiosError;
            if (isMock(error) && !!config.mockLocal.recordUploaded) {
                onSuccess();
            } else {
                if (error.response?.status === 403) {
                    navigate(routes.SESSION_EXPIRED);
                } else {
                    navigate(routes.SERVER_ERROR + errorToParams(error));
                }
                setDeletionStage(SUBMISSION_STATE.FAILED);
            }
        }
    };

    const handleNoOption = () => {
        if (role === REPOSITORY_ROLE.GP_ADMIN) {
            navigate(routes.LLOYD_GEORGE);
        } else if (role === REPOSITORY_ROLE.PCSE && setIsDeletingDocuments) {
            navigate(routes.ARF_OVERVIEW);
        }
    };

    const submit = async (fieldValues: FieldValues) => {
        const allowedRoles = [REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.PCSE];
        if (role && allowedRoles.includes(role)) {
            if (fieldValues.deleteDocs === DELETE_DOCUMENTS_OPTION.YES) {
                await handleYesOption();
            } else if (fieldValues.deleteDocs === DELETE_DOCUMENTS_OPTION.NO) {
                handleNoOption();
            } else {
                setShowNoOptionSelectedMessage(true);
            }
        }
    };
    useTitle({ pageTitle: 'Delete files' });

    return (
        <>
            <div>
                <Routes>
                    <Route
                        index
                        element={
                            <>
                                <BackLink onClick={handleNoOption} href="#">
                                    Back
                                </BackLink>
                                {deletionStage === SUBMISSION_STATE.FAILED && <ServiceError />}
                                {showNoOptionSelectedMessage && (
                                    <ErrorBox
                                        messageTitle={'There is a problem '}
                                        messageLinkBody={'You must select an option'}
                                        errorBoxSummaryId={'error-box-summary'}
                                        errorInputLink={'#delete-docs'}
                                        dataTestId={'delete-error-box'}
                                    />
                                )}
                                <form onSubmit={handleSubmit(submit)}>
                                    <Fieldset id="radio-selection">
                                        <Fieldset.Legend isPageHeading>
                                            Are you sure you want to permanently delete files for:
                                        </Fieldset.Legend>
                                        <div>{patientInfo}</div>
                                        <Radios
                                            id="delete-docs"
                                            error={
                                                showNoOptionSelectedMessage && noOptionSelectedError
                                            }
                                        >
                                            <Radios.Radio
                                                value={DELETE_DOCUMENTS_OPTION.YES}
                                                inputRef={deleteDocsRef}
                                                {...radioProps}
                                                id="yes-radio-button"
                                                data-testid="yes-radio-btn"
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
                                        <SpinnerButton
                                            id="delete-docs-spinner"
                                            status="Deleting..."
                                            disabled={true}
                                        />
                                    ) : (
                                        <Button
                                            type="submit"
                                            id="delete-submit-button"
                                            data-testid="delete-submit-btn"
                                        >
                                            Continue
                                        </Button>
                                    )}
                                </form>
                            </>
                        }
                    />
                    <Route
                        path="complete"
                        element={
                            <DeletionConfirmationStage
                                numberOfFiles={numberOfFiles}
                                setStage={setStage}
                                setDownloadStage={setDownloadStage}
                            />
                        }
                    />
                </Routes>

                <Outlet />
            </div>
        </>
    );
}
export default DeleteDocumentsStage;
