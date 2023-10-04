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
    const lgRegex =
        /[0-9]+of[0-9]+_Lloyd_George_Record_\[[A-Za-z]+\s[A-Za-z]+]_\[[0-9]{10}]_\[\d\d-\d\d-\d\d\d\d].pdf/; // eslint-disable-line
    const lgFilesNumber = /of[0-9]+/;
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
                            const currentFile = value[i].file;
                            if (currentFile.size > FIVEGB) {
                                return 'Please ensure that all files are less than 5GB in size';
                            }
                            if (name === 'lg-documents') {
                                if (currentFile.type !== 'application/pdf') {
                                    return 'One or more of the files do not match the required file type. Please check the file(s) and try again';
                                }
                                const expectedNumberOfFiles = currentFile.name.match(lgFilesNumber);
                                const doesPassRegex = lgRegex.exec(currentFile.name);
                                const doFilesTotalMatch =
                                    expectedNumberOfFiles &&
                                    value.length == parseInt(expectedNumberOfFiles[0].slice(2));
                                const isFileNumberBiggerThanTotal =
                                    expectedNumberOfFiles &&
                                    parseInt(currentFile.name.split(lgFilesNumber)[0]) >
                                        parseInt(expectedNumberOfFiles[0].slice(2));
                                const isFileNumberZero =
                                    currentFile.name.split(lgFilesNumber)[0] === '0';
                                const doesFileNameMatchEachOther =
                                    currentFile.name.split(lgFilesNumber)[1] ==
                                    value[0].file.name.split(lgFilesNumber)[1];
                                if (
                                    !doesPassRegex ||
                                    !doFilesTotalMatch ||
                                    isFileNumberBiggerThanTotal ||
                                    isFileNumberZero ||
                                    !doesFileNameMatchEachOther
                                ) {
                                    return 'One or more of the files do not match the required filename format. Please check the file(s) and try again';
                                }
                            }
                        }
                    }
                },
                hasDuplicateFile: (value?: Array<UploadDocument>) => {
                    if (
                        name === 'lg-documents' &&
                        value?.some((doc: UploadDocument) => {
                            return value?.some(
                                (compare: UploadDocument) =>
                                    doc.file.name === compare.file.name &&
                                    doc.file.size === compare.file.size &&
                                    doc.id !== compare.id,
                            );
                        })
                    ) {
                        return 'There are documents chosen that have the same name, a record with duplicate file names can not be uploaded because it does not match the required file format. Please check the files(s) and try again.';
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
                arfController.field.onChange(updatedDocList);
            }
        } else {
            setLgDocuments(updatedDocList);
            if (lgInputRef.current) {
                lgInputRef.current.files = toFileList(updatedDocList);
                lgController.field.onChange(updatedDocList);
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
                <Fieldset.Legend headingLevel="h1" isPageHeading>
                    Upload documents
                </Fieldset.Legend>
                <PatientSummary patientDetails={patientDetails} />

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
                <Fieldset>
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
