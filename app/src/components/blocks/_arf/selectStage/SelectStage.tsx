import React, { useRef } from 'react';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    FileInputEvent,
    SetUploadDocuments,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { Button, Fieldset } from 'nhsuk-react-components';
import { useController, useForm } from 'react-hook-form';
import toFileList from '../../../../helpers/utils/toFileList';
import DocumentInputForm from '../documentInputForm/DocumentInputForm';
import { ARFFormConfig } from '../../../../helpers/utils/formConfig';
import { v4 as uuidv4 } from 'uuid';
import uploadDocuments from '../../../../helpers/requests/uploadDocuments';
import usePatient from '../../../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import BackButton from '../../../generic/backButton/BackButton';
import { UploadSession } from '../../../../types/generic/uploadResult';
import { AxiosError } from 'axios';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import { isMock } from '../../../../helpers/utils/isLocal';
import { useNavigate } from 'react-router';
import PatientSummary from '../../../generic/patientSummary/PatientSummary';
import {
    markDocumentsAsUploading,
    uploadAndScanSingleDocument,
    setSingleDocument,
} from '../../../../helpers/utils/uploadAndScanDocumentHelpers';

interface Props {
    setDocuments: SetUploadDocuments;
    documents: Array<UploadDocument>;
}

function SelectStage({ setDocuments, documents }: Props) {
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const navigate = useNavigate();
    const arfInputRef = useRef<HTMLInputElement | null>(null);
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const hasFileInput = documents.length > 0;

    const { handleSubmit, control, formState, setError } = useForm();

    const arfController = useController(ARFFormConfig(control));

    const submitDocuments = async () => {
        if (!hasFileInput) {
            setError('arf-documents', { type: 'custom', message: 'Select a file to upload' });
            return;
        }

        navigate(routeChildren.ARF_UPLOAD_UPLOADING);
        try {
            const uploadSession = await uploadDocuments({
                nhsNumber,
                documents,
                baseUrl,
                baseHeaders,
            });
            const uploadingDocuments: UploadDocument[] = markDocumentsAsUploading(
                documents,
                uploadSession,
            );
            setDocuments(uploadingDocuments);

            uploadAndScanAllDocuments(uploadingDocuments, uploadSession);
        } catch (error) {
            handleUploadError(error as AxiosError);
        }
    };

    const uploadAndScanAllDocuments = (
        uploadingDocuments: UploadDocument[],
        uploadSession: UploadSession,
    ) => {
        uploadingDocuments.forEach((document) => {
            void uploadAndScanSingleArfDocument(document, uploadSession);
        });
    };

    const uploadAndScanSingleArfDocument = async (
        document: UploadDocument,
        uploadSession: UploadSession,
    ) => {
        try {
            await uploadAndScanSingleDocument({
                document,
                uploadSession,
                setDocuments,
                baseUrl,
                baseHeaders,
            });
        } catch (e) {
            markDocumentAsFailed(document);
        }
    };

    const handleUploadError = (error: AxiosError) => {
        if (error.response?.status === 403) {
            navigate(routes.SESSION_EXPIRED);
        } else if (isMock(error)) {
            /* istanbul ignore next */
            setDocuments((prevState) =>
                prevState.map((doc) => ({
                    ...doc,
                    state: DOCUMENT_UPLOAD_STATE.CLEAN,
                })),
            );
        } else {
            navigate(routes.SERVER_ERROR + errorToParams(error));
        }
    };

    const markDocumentAsFailed = (failedDocument: UploadDocument) => {
        setSingleDocument(setDocuments, {
            id: failedDocument.id,
            state: DOCUMENT_UPLOAD_STATE.FAILED,
            progress: 0,
        });
    };

    const onInput = (e: FileInputEvent, docType: DOCUMENT_TYPE) => {
        const fileArray = Array.from(e.target.files ?? new FileList());
        const newlyAddedDocuments: Array<UploadDocument> = fileArray.map((file) => ({
            id: uuidv4(),
            file,
            state: DOCUMENT_UPLOAD_STATE.SELECTED,
            progress: 0,
            docType: docType,
            attempts: 0,
        }));
        const updatedDocList = [...newlyAddedDocuments, ...documents];
        arfController.field.onChange(updatedDocList);
        setDocuments(updatedDocList);
    };

    const onRemove = (index: number, _docType: DOCUMENT_TYPE) => {
        const updatedDocList: UploadDocument[] = [
            ...documents.slice(0, index),
            ...documents.slice(index + 1),
        ];

        if (arfInputRef.current) {
            arfInputRef.current.files = toFileList(updatedDocList);
            arfController.field.onChange(updatedDocList);
        }

        setDocuments(updatedDocList);
    };

    return (
        <>
            <BackButton />
            <form
                onSubmit={handleSubmit(submitDocuments)}
                noValidate
                data-testid="upload-document-form"
            >
                <Fieldset.Legend
                    headingLevel="h1"
                    isPageHeading
                    data-testid="arf-upload-select-stage-header"
                >
                    Upload documents
                </Fieldset.Legend>
                <PatientSummary />

                <Fieldset>
                    <h2>Electronic health records</h2>
                    <DocumentInputForm
                        showHelp
                        documents={documents}
                        onDocumentRemove={onRemove}
                        onDocumentInput={onInput}
                        formController={arfController}
                        inputRef={arfInputRef}
                        formType={DOCUMENT_TYPE.ARF}
                    />
                </Fieldset>
                <Button
                    type="submit"
                    id="upload-button"
                    data-testid="arf-upload-submit-btn"
                    disabled={formState.isSubmitting}
                >
                    Upload
                </Button>
            </form>
        </>
    );
}

export default SelectStage;
