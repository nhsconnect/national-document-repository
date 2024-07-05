export enum JOB_STATUS {
    PENDING = 'Pending',
    COMPLETED = 'Completed',
    PROCESSING = 'Processing',
}

export type PollingResponse = Completed | Pending | Processing;

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
