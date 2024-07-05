export enum JOB_STATUS {
    PENDING = 'Pending',
    COMPLETED = 'Completed',
    PROCESSING = 'Processing',
}

export type PollingResponse = Completed | Pending | Processing;

type Completed = {
    job_status: JOB_STATUS.COMPLETED;
    url: string;
};

type Pending = {
    job_status: JOB_STATUS.PENDING;
};

type Processing = {
    job_status: JOB_STATUS.PROCESSING;
};
