import React, { Dispatch, SetStateAction, useRef } from 'react';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    FileInputEvent,
    SetUploadDocuments,
    UPLOAD_STAGE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { Button, Fieldset } from 'nhsuk-react-components';
import { useController, useForm } from 'react-hook-form';
import toFileList from '../../../../helpers/utils/toFileList';
import PatientDetails from '../../../generic/patientDetails/PatientDetails';
import DocumentInputForm from '../documentInputForm/DocumentInputForm';
import { ARFFormConfig } from '../../../../helpers/utils/formConfig';
import { v4 as uuidv4 } from 'uuid';
import uploadDocuments, { uploadDocumentToS3 } from '../../../../helpers/requests/uploadDocuments';
import usePatient from '../../../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import BackButton from '../../../generic/backButton/BackButton';
import { UploadSession } from '../../../../types/generic/uploadResult';
import { AxiosError } from 'axios';
import { routes } from '../../../../types/generic/routes';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import { isMock } from '../../../../helpers/utils/isLocal';
import { useNavigate } from 'react-router';

interface Props {
    setDocuments: SetUploadDocuments;
    setStage: Dispatch<SetStateAction<UPLOAD_STAGE>>;
    documents: Array<UploadDocument>;
}

function SelectStage({ setDocuments, setStage, documents }: Props) {
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

        setStage(UPLOAD_STAGE.Uploading);
        try {
            const uploadSession = await uploadDocuments({
                nhsNumber,
                documents,
                baseUrl,
                baseHeaders,
            });
            const uploadingDocuments: UploadDocument[] =
                addMetadataAndMarkDocumentAsUploading(uploadSession);
            setDocuments(uploadingDocuments);

            await uploadAllDocumentsToS3(uploadingDocuments, uploadSession);

            setStage(UPLOAD_STAGE.Complete);
        } catch (error) {
            handleUploadError(error as AxiosError);
        }
    };

    const markDocumentAsFailed = (failedDocument: UploadDocument) => {
        setDocuments((prevState) =>
            prevState.map((prevStateDocument) => {
                if (prevStateDocument.id !== failedDocument.id) {
                    return prevStateDocument;
                }
                return { ...prevStateDocument, state: DOCUMENT_UPLOAD_STATE.FAILED, progress: 0 };
            }),
        );
    };

    const uploadAllDocumentsToS3 = (
        uploadingDocuments: UploadDocument[],
        uploadSession: UploadSession,
    ) => {
        const allUploadPromises = uploadingDocuments.map((document) =>
            uploadDocumentToS3({ setDocuments, document, uploadSession }).catch(() =>
                markDocumentAsFailed(document),
            ),
        );
        return Promise.all(allUploadPromises);
    };

    const handleUploadError = (error: AxiosError) => {
        if (error.response?.status === 403) {
            navigate(routes.SESSION_EXPIRED);
        } else if (isMock(error)) {
            /* istanbul ignore next */
            setDocuments((prevState) =>
                prevState.map((doc) => ({
                    ...doc,
                    state: DOCUMENT_UPLOAD_STATE.SUCCEEDED,
                })),
            );
            /* istanbul ignore next */
            setStage(UPLOAD_STAGE.Complete);
        } else {
            navigate(routes.SERVER_ERROR + errorToParams(error));
        }
    };

    const addMetadataAndMarkDocumentAsUploading = (uploadSession: UploadSession) => {
        return documents.map((doc) => {
            const documentMetadata = uploadSession[doc.file.name];
            const documentReference = documentMetadata.fields.key;
            return {
                ...doc,
                state: DOCUMENT_UPLOAD_STATE.UPLOADING,
                key: documentReference,
                ref: documentReference.split('/').at(-1),
            };
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
                <Fieldset.Legend headingLevel="h1" isPageHeading>
                    Upload documents
                </Fieldset.Legend>
                <PatientDetails />

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
                <Button type="submit" id="upload-button" disabled={formState.isSubmitting}>
                    Upload
                </Button>
            </form>
        </>
    );
}

export default SelectStage;
