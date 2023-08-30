import React, { useRef } from "react";
import type { FormEvent, MouseEvent } from "react";
import {
  DOCUMENT_UPLOAD_STATE,
  SetUploadDocuments,
  UploadDocument,
} from "../../../types/pages/UploadDocumentsPage/types";
import { Button, Fieldset, Input, Table, WarningCallout } from "nhsuk-react-components";
import { useController, useForm } from "react-hook-form";
import formatFileSize from "../../../helpers/utils/formatFileSize";
import toFileList from "../../../helpers/utils/toFileList";
import PatientSummary from "../../patientSummary/PatientSummary";
import { PatientDetails } from "../../../types/components/types";
interface FileInputEvent extends FormEvent<HTMLInputElement> {
    target: HTMLInputElement & EventTarget;
}

interface Props {
    uploadDocuments: () => void;
    setDocuments: SetUploadDocuments;
}

function SelectStage({
  uploadDocuments,
  setDocuments,
}: Props) {
  let inputRef = useRef<HTMLInputElement | null>(null);
  const FIVEGB = 5 * Math.pow(1024, 3);
  const { handleSubmit, control, formState } = useForm();
  const {
    field: { ref, onChange, onBlur, name, value },
    fieldState,
  } = useController({
    name: "documents",
    control,
    rules: {
      validate: {
        isFile: (value) => {
          return (value && value.length > 0) || "Please select a file";
        },
        isLessThan5GB: (value) => {
          for (let i = 0; i < value.length; i++) {
            if (value[i].file.size > FIVEGB) {
              return "Please ensure that all files are less than 5GB in size";
            }
          }
        },
      },
    },
  });

    const hasDuplicateFiles =
        value &&
        value.some((doc: UploadDocument) => {
            return value.some(
                (compare: UploadDocument) =>
                    doc.file.name === compare.file.name && doc.id !== compare.id
            );
        });

    const onInput = (e: FileInputEvent) => {
        const fileArray = Array.from(e.target.files ?? new FileList());
        const documentMap: Array<UploadDocument> = fileArray.map((file) => ({
            id: (Math.floor(Math.random() * 1000000)).toString(),
            file,
            state: DOCUMENT_UPLOAD_STATE.SELECTED,
            progress: 0,
        }));

        const updatedFileList = value ? [...value, ...documentMap] : documentMap;
        onChange(updatedFileList);
        setDocuments(updatedFileList);
    };

    const onRemove = (index: number) => {
        const updatedValues = [...value.slice(0, index), ...value.slice(index + 1)];
        onChange(updatedValues);
        setDocuments(updatedValues)
        if (inputRef.current) {
            inputRef.current.files = toFileList(updatedValues);
        }
    };

    const mockPatientDetails: Partial<PatientDetails> = {
        nhsNumber: "111111111",
        familyName: "test",
        givenName: ["Gremlin", "Junior"],
        birthDate: "5/12/2022",
        postalCode: "BS37 5DH",
    }

    return (
        <>
            <form onSubmit={handleSubmit(uploadDocuments)} noValidate data-testid="upload-document-form">
                <Fieldset>
                    <Fieldset.Legend headingLevel="h1" isPageHeading>
                        Upload documents
                    </Fieldset.Legend>
                    <PatientSummary patientDetails={mockPatientDetails}/>
                    <Input
                        id="documents-input"
                        label="Select file(s)"
                        type="file"
                        multiple={true}
                        name={name}
                        error={fieldState.error?.message}
                        onChange={onInput}
                        onBlur={onBlur}
                        // @ts-ignore  The NHS Component library is outdated and does not allow for any reference other than a blank MutableRefObject
                        inputRef={(e: HTMLInputElement) => {
                            ref(e);
                            inputRef.current = e;
                        }}
                        // @ts-ignore
                        hint={
                            <ul>
                                <li>{"A patient's full electronic health record including attachments must be uploaded."}</li>
                                <li>{"You can select multiple files to upload at once."}</li>
                                <li>
                                    In the event documents cannot be uploaded, they must be printed and sent via{" "}
                                    <a href="https://secure.pcse.england.nhs.uk/" target="_blank" rel="noreferrer">
                                        Primary Care Support England
                                    </a>
                                    .
                                </li>
                            </ul>
                        }
                    />
                    <div role="region" aria-live="polite">
                        {value && value.length > 0 && (
                            <Table caption="Selected documents">
                                <Table.Head>
                                    <Table.Row>
                                        <Table.Cell>Filename</Table.Cell>
                                        <Table.Cell>Size</Table.Cell>
                                        <Table.Cell>Remove</Table.Cell>
                                    </Table.Row>
                                </Table.Head>

                                <Table.Body>
                                    {value.map((document: UploadDocument, index: number) => (
                                        <Table.Row key={document.id}>
                                            <Table.Cell>{document.file.name}</Table.Cell>
                                            <Table.Cell>{formatFileSize(document.file.size)}</Table.Cell>
                                            <Table.Cell>
                                                <a
                                                    aria-label={`Remove ${document.file.name} from selection`}
                                                    href="#"
                                                    onClick={(e: MouseEvent<HTMLElement>) => {
                                                        e.preventDefault();
                                                        onRemove(index);
                                                    }}
                                                >
                                                    Remove
                                                </a>
                                            </Table.Cell>
                                        </Table.Row>
                                    ))}
                                </Table.Body>
                            </Table>
                        )}
                        {hasDuplicateFiles && (
                            <WarningCallout>
                                <WarningCallout.Label>Possible duplicate file</WarningCallout.Label>
                                <p>There are two or more documents with the same name.</p>
                                <p>Are you sure you want to proceed?</p>
                            </WarningCallout>
                        )}
                    </div>
                </Fieldset>
                <Button type="submit" disabled={formState.isSubmitting || !value}>
                    Upload
                </Button>
            </form>
        </>
    );
}

export default SelectStage;
