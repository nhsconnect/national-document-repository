import React, { useRef } from 'react';
import type { FormEvent as ReactEvent } from 'react';
import {
  DOCUMENT_UPLOAD_STATE,
  StageProps
} from '../../../types/pages/UploadDocumentsPage/types';
import { Button, Input } from 'nhsuk-react-components';
import { useController, useForm } from 'react-hook-form';
import { nanoid } from 'nanoid/non-secure';

interface FileInputEvent extends ReactEvent<HTMLInputElement> {
  target: HTMLInputElement & EventTarget;
}

function SelectStage({ stage, setStage, uploadDocuments }: StageProps) {
  const inputRef = useRef(null);
  const FIVEGB = 5 * Math.pow(1024, 3);
  const { handleSubmit, control, watch, getValues, formState, setValue } =
    useForm();
  const {
    field: { ref, onChange, onBlur, name, value },
    fieldState
  } = useController({
    name: 'documents',
    control,
    rules: {
      validate: {
        isFile: (value) => {
          return (value && value.length > 0) || 'Please select a file';
        },
        isLessThan5GB: (value) => {
          for (let i = 0; i < value.length; i++) {
            if (value[i].file.size > FIVEGB) {
              return 'Please ensure that all files are less than 5GB in size';
            }
          }
        }
      }
    }
  });

  const fileHandler = (e: FileInputEvent) => {
    const fileArray = Array.from(e.target.files ?? new FileList());
    const documentMap = fileArray.map((file) => ({
      id: nanoid(),
      file,
      state: DOCUMENT_UPLOAD_STATE.SELECTED,
      progress: 0
    }));

    const updatedFileList = value ? [...value, ...documentMap] : documentMap;
    onChange(updatedFileList);
  };

  return (
    <>
      <Input
        id='documents-input'
        label='Select file(s)'
        type='file'
        multiple={true}
        name={name}
        error={fieldState.error?.message}
        onChange={fileHandler}
        onBlur={onBlur}
        inputRef={inputRef}
      />

      <Button onClick={uploadDocuments}>Upload</Button>
    </>
  );
}

export default SelectStage;
