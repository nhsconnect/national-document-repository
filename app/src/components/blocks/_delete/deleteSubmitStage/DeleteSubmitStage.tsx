import React, { Dispatch, SetStateAction, useState } from 'react';
import { FieldValues, useForm } from 'react-hook-form';
import { BackLink, Button, Fieldset, Radios } from 'nhsuk-react-components';
import deleteAllDocuments, {
    DeleteResponse,
} from '../../../../helpers/requests/deleteAllDocuments';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import { DOCUMENT_TYPE } from '../../../../types/pages/UploadDocumentsPage/types';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import SpinnerButton from '../../../generic/spinnerButton/SpinnerButton';
import ServiceError from '../../../layout/serviceErrorBox/ServiceErrorBox';
import { SUBMISSION_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import { AxiosError } from 'axios';
import { routes } from '../../../../types/generic/routes';
import { useNavigate } from 'react-router-dom';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import usePatient from '../../../../helpers/hooks/usePatient';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import { isMock } from '../../../../helpers/utils/isLocal';
import useConfig from '../../../../helpers/hooks/useConfig';
import useTitle from '../../../../helpers/hooks/useTitle';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import DeleteResultStage from '../deleteResultStage/DeleteResultStage';
import WarningText from '../../../generic/warningText/WarningText';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';

export type Props = {
    docType: DOCUMENT_TYPE;
    numberOfFiles: number;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    setIsDeletingDocuments?: Dispatch<SetStateAction<boolean>>;
    setDownloadStage?: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
    recordType: string;
};

enum DELETE_DOCUMENTS_OPTION {
    YES = 'yes',
    NO = 'no',
}

function DeleteSubmitStage({
    docType,
    numberOfFiles,
    setStage,
    setIsDeletingDocuments,
    setDownloadStage,
    recordType,
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
    const [showNoOptionSelectedMessage, setShowNoOptionSelectedMessage] = useState<boolean>(false);
    const noOptionSelectedError =
        'Select whether you want to permanently delete these patient files';

    const handleYesOption = async () => {
        setDeletionStage(SUBMISSION_STATE.PENDING);
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
            } else {
                setShowNoOptionSelectedMessage(true);
            }
        }
    };
    useTitle({ pageTitle: 'Delete files' });

    return deletionStage !== SUBMISSION_STATE.SUCCEEDED ? (
        <>
            <BackLink onClick={handleNoOption} href="#">
                Go back
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
                        You are removing the {recordType} record of:
                    </Fieldset.Legend>
                    <PatientSimpleSummary separator />

                    <p>
                        Once you remove this files, you can not access this record using the
                        service. you may want to keep a copy of the paper record safe.
                    </p>
                    <h2 test-dataid="delete-files-warning-message">
                        Are you sure you want to permanently remove this record?
                    </h2>
                    <div>
                        <WarningText text="This can not be undone" />
                    </div>
                    <Radios
                        id="delete-docs"
                        error={showNoOptionSelectedMessage && noOptionSelectedError}
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
                    <SpinnerButton id="delete-docs-spinner" status="Deleting..." disabled={true} />
                ) : (
                    <Button type="submit" id="delete-submit-button" data-testid="delete-submit-btn">
                        Continue
                    </Button>
                )}
            </form>
        </>
    ) : (
        <DeleteResultStage
            numberOfFiles={numberOfFiles}
            setStage={setStage}
            setDownloadStage={setDownloadStage}
        />
    );
}
export default DeleteSubmitStage;
