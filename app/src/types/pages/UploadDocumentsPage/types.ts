import type { Dispatch, FormEvent, SetStateAction } from 'react';
import { UPLOAD_FILE_ERROR_TYPE } from '../../../helpers/utils/fileUploadErrorMessages';

export type SetUploadStage = Dispatch<SetStateAction<UPLOAD_STAGE>>;
export type SetUploadDocuments = Dispatch<SetStateAction<Array<UploadDocument>>>;

export enum UPLOAD_STAGE {
    Selecting = 0,
    Uploading = 1,
    Complete = 2,
}

export enum DOCUMENT_TYPE {
    LLOYD_GEORGE = 'LG',
    ARF = 'ARF',
    ALL = 'LG,ARF',
}

export enum DOCUMENT_UPLOAD_STATE {
    SELECTED = 'SELECTED',
    UPLOADING = 'UPLOADING',
    SUCCEEDED = 'SUCCEEDED',
    FAILED = 'FAILED',
    UNAUTHORISED = 'UNAUTHORISED',
    SCANNING = 'SCANNING',
    CLEAN = 'CLEAN',
    INFECTED = 'INFECTED',
}

export type UploadDocument = {
    state: DOCUMENT_UPLOAD_STATE;
    file: File;
    progress?: number;
    id: string;
    docType: DOCUMENT_TYPE;
    attempts: number;
    ref?: string;
    key?: string;
};

export type UploadFilesErrors = {
    filename?: string;
    error: UPLOAD_FILE_ERROR_TYPE;
    details?: string;
};

export type SearchResult = {
    id: string;
    description: string;
    type: string;
    indexed: Date;
    virusScanResult: string;
};

export interface FileInputEvent extends FormEvent<HTMLInputElement> {
    target: HTMLInputElement & EventTarget;
}
