export enum JOB_STATUS {
    PENDING = 'Pending',
    COMPLETED = 'Completed',
    PROCESSING = 'Processing',
    FAILED = 'Failed',
}

export type PollingResponse = Completed | Pending | Processing | Failed;

type Completed = {
    status: JOB_STATUS.COMPLETED;
    url: string;
};

type Pending = {
    status: JOB_STATUS.PENDING;
};

type Processing = {
    status: JOB_STATUS.PROCESSING;
};

type Failed = {
    status: JOB_STATUS.FAILED;
};
