import type { Dispatch, SetStateAction } from 'react';
export enum SEARCH_STATES {
    IDLE = 'idle',
    SEARCHING = 'searching',
    SUCCEEDED = 'succeeded',
    FAILED = 'failed',
}

export type SetSubmissionState = Dispatch<SetStateAction<SEARCH_STATES>>;
export type SetSearchErrorCode = Dispatch<SetStateAction<number | null>>;
