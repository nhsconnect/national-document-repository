import React, { useRef, useState } from 'react';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    FileInputEvent,
    SetUploadDocuments,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import { Button, Fieldset } from 'nhsuk-react-components';
import { useController, useForm } from 'react-hook-form';
import toFileList from '../../../helpers/utils/toFileList';
import PatientSummary from '../../generic/patientSummary/PatientSummary';
import { PatientDetails } from '../../../types/generic/patientDetails';
import DocumentInputForm from '../documentInputForm/DocumentInputForm';

interface Props {
    uploadDocuments: () => void;
    setDocuments: SetUploadDocuments;
    patientDetails: PatientDetails;
}

function SelectStage({ uploadDocuments, setDocuments, patientDetails }: Props) {
    const [arfDocuments, setArfDocuments] = useState<Array<UploadDocument>>([]);
    const [lgDocuments, setLgDocuments] = useState<Array<UploadDocument>>([]);

    let arfInputRef = useRef<HTMLInputElement | null>(null);
    let lgInputRef = useRef<HTMLInputElement | null>(null);

    const mergedDocuments = [...arfDocuments, ...lgDocuments];
    const hasFileInput = mergedDocuments.length;
    const lgRegex = /[0-9]+of[0-9]+_Lloyd_George_Record_\[[A-Za-z]+\s[A-Za-z]+]_\[[0-9]{10}]_\[\d\d-\d\d-\d\d\d\d]/;


    const FIVEGB = 5 * Math.pow(1024, 3);
    const { handleSubmit, control, formState } = useForm();
    const formConfig = (name: string) => ({
        name,
        control,
        rules: {
            validate: {
                isFile: () => {
                    return !!hasFileInput || 'Please select a file';
                },
                perFileValidation: (value?: Array<UploadDocument>) => {
                    if (Array.isArray(value)) {
                        for (let i = 0; i < value.length; i++) {
                            if (value[i].file.size > FIVEGB) {
                                return 'Please ensure that all files are less than 5GB in size';
                            }
                            if (name === 'lg-documents' && value[i].file.type == 'application/pdf') {
                                return 'Please ensure that all files are PDF files';
                            }
                            if (name === 'lg-documents' && !lgRegex.exec(value[i].file.name)) {
                                return 'One or more of the files do not match the required filename format. Please check the file(s) and try again';
                            }
                        }
                    }
                },
            },
        },
    });
    const lgController = useController(formConfig('lg-documents'));
    const arfController = useController(formConfig('arf-documents'));

    const onInput = (e: FileInputEvent, docType: DOCUMENT_TYPE) => {
        const fileArray = Array.from(e.target.files ?? new FileList());
        const documentMap: Array<UploadDocument> = fileArray.map((file) => ({
            id: Math.floor(Math.random() * 1000000).toString(),
            file,
            state: DOCUMENT_UPLOAD_STATE.SELECTED,
            progress: 0,
            docType: docType,
        }));
        const isArfDoc = docType === DOCUMENT_TYPE.ARF;
        const mergeList = isArfDoc ? lgDocuments : arfDocuments;
        const docTypeList = isArfDoc ? arfDocuments : lgDocuments;
        const updatedDocList = [...documentMap, ...docTypeList];
        if (isArfDoc) {
            setArfDocuments(updatedDocList);
            arfController.field.onChange(updatedDocList);
        } else {
            setLgDocuments(updatedDocList);
            lgController.field.onChange(updatedDocList);
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
            }
        } else {
            setLgDocuments(updatedDocList);
            if (lgInputRef.current) {
                lgInputRef.current.files = toFileList(updatedDocList);
            }
        }

        const updatedFileList = [...mergeList, ...updatedDocList];
        setDocuments(updatedFileList);
    };

    return (
        <>
            <form
                onSubmit={handleSubmit(uploadDocuments)}
                noValidate
                data-testid="upload-document-form"
            >
                <Fieldset>
                    <Fieldset.Legend headingLevel="h1" isPageHeading>
                        Upload documents
                    </Fieldset.Legend>
                    <PatientSummary patientDetails={patientDetails} />
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
                    <br />
                    <br />
                    <h2>Lloyd George records</h2>
                    <DocumentInputForm
                        documents={lgDocuments}
                        onDocumentRemove={onRemove}
                        onDocumentInput={onInput}
                        formController={lgController}
                        inputRef={lgInputRef}
                        formType={DOCUMENT_TYPE.LLOYD_GEORGE}
                    />
                </Fieldset>
                <Button
                    type="submit"
                    id="upload-button"
                    disabled={formState.isSubmitting || !hasFileInput}
                >
                    Upload
                </Button>
            </form>
        </>
    );
}

export default SelectStage;
