import type { Dispatch, FormEvent, SetStateAction } from 'react';

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
    progress: number | undefined;
    id: string;
    docType: DOCUMENT_TYPE;
    attempts: number;
};

export type UploadFilesErrors = {
    file?: UploadDocument;
    error: Record<string, string>;
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
