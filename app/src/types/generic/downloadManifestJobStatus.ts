export enum JOB_STATUS {
    PENDING = 'Pending',
    COMPLETED = 'Completed',
    PROCESSING = 'Processing',
    FAILED = 'Failed',
}

export type PollingResponse = Completed | Pending | Processing | Failed;

type Completed = {
    jobStatus: JOB_STATUS.COMPLETED;
    url: string;
};

type Pending = {
    jobStatus: JOB_STATUS.PENDING;
};

type Processing = {
    jobStatus: JOB_STATUS.PROCESSING;
};

type Failed = {
    jobStatus: JOB_STATUS.FAILED;
};
