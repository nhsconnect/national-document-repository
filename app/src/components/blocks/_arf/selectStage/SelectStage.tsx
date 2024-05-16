import React, { Dispatch, SetStateAction, useRef, useState } from 'react';
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
import PatientSummary from '../../../generic/patientSummary/PatientSummary';
import DocumentInputForm from '../documentInputForm/DocumentInputForm';
import { ARFFormConfig } from '../../../../helpers/utils/formConfig';
import { v4 as uuidv4 } from 'uuid';
import uploadDocuments, { uploadDocumentToS3 } from '../../../../helpers/requests/uploadDocuments';
import usePatient from '../../../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import BackButton from '../../../generic/backButton/BackButton';
import { setDocument } from '../../../../pages/lloydGeorgeUploadPage/LloydGeorgeUploadPage';
import { UploadSession } from '../../../../types/generic/uploadResult';

interface Props {
    setDocuments: SetUploadDocuments;
    setStage: Dispatch<SetStateAction<UPLOAD_STAGE>>;
    documents: Array<UploadDocument>;
}

function SelectStage({ setDocuments, setStage, documents }: Props) {
    const [arfDocuments, setArfDocuments] = useState<Array<UploadDocument>>([]);
    const [lgDocuments, setLgDocuments] = useState<Array<UploadDocument>>([]);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const arfInputRef = useRef<HTMLInputElement | null>(null);
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const mergedDocuments = [...arfDocuments, ...lgDocuments];
    const hasFileInput = mergedDocuments.length;

    const { handleSubmit, control, formState, setError } = useForm();

    const arfController = useController(ARFFormConfig(control));

    const markDocumentAsFailed = (document: UploadDocument) => {
        setDocuments((prevState) =>
            prevState.map((prevStateDocument) => {
                if (prevStateDocument.id !== document.id) {
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
            const uploadingDocuments: UploadDocument[] = documents.map((doc) => {
                const documentMetadata = uploadSession[doc.file.name];
                const documentReference = documentMetadata.fields.key;
                return {
                    ...doc,
                    state: DOCUMENT_UPLOAD_STATE.UPLOADING,
                    key: documentReference,
                    ref: documentReference.split('/')[3],
                };
            });
            setDocuments(uploadingDocuments);

            await uploadAllDocumentsToS3(uploadingDocuments, uploadSession);
        } catch (e) {}
        setStage(UPLOAD_STAGE.Complete);
    };
    const onInput = (e: FileInputEvent, docType: DOCUMENT_TYPE) => {
        const fileArray = Array.from(e.target.files ?? new FileList());
        const documentMap: Array<UploadDocument> = fileArray.map((file) => ({
            id: uuidv4(),
            file,
            state: DOCUMENT_UPLOAD_STATE.SELECTED,
            progress: 0,
            docType: docType,
            attempts: 0,
        }));
        const isArfDoc = docType === DOCUMENT_TYPE.ARF;
        const mergeList = isArfDoc ? lgDocuments : arfDocuments;
        const docTypeList = isArfDoc ? arfDocuments : lgDocuments;
        const updatedDocList = [...documentMap, ...docTypeList];
        if (isArfDoc) {
            setArfDocuments(updatedDocList);
            arfController.field.onChange(updatedDocList);
        }
        const updatedFileList = [...mergeList, ...updatedDocList];
        setDocuments(updatedFileList);
    };

    const onRemove = (index: number, docType: DOCUMENT_TYPE) => {
        const isArfDoc = docType === DOCUMENT_TYPE.ARF;
        const mergeList = isArfDoc ? lgDocuments : arfDocuments;
        const docTypeList = isArfDoc ? arfDocuments : lgDocuments;
        const updatedDocList = [...docTypeList.slice(0, index), ...docTypeList.slice(index + 1)];
        if (isArfDoc) {
            setArfDocuments(updatedDocList);
            if (arfInputRef.current) {
                arfInputRef.current.files = toFileList(updatedDocList);
                arfController.field.onChange(updatedDocList);
            }

            const updatedFileList = [...mergeList, ...updatedDocList];
            setDocuments(updatedFileList);
        }
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
                <PatientSummary />

                <Fieldset>
                    <h2>Electronic health records</h2>
                    <DocumentInputForm
                        showHelp
                        documents={arfDocuments}
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
