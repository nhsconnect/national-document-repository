import { REPOSITORY_ROLE } from '../generic/authRole';
import { LG_RECORD_STAGE } from './lloydGeorgeStages';

type PdfActionLink = {
    label: string;
    key: string;
    stage: LG_RECORD_STAGE;
    unauthorised?: Array<REPOSITORY_ROLE>;
};

export const actionLinks: Array<PdfActionLink> = [
    {
        label: 'See all files',
        key: 'see-all-files-link',
        stage: LG_RECORD_STAGE.SEE_ALL,
    },
    {
        label: 'Download all files',
        key: 'download-all-files-link',
        stage: LG_RECORD_STAGE.DOWNLOAD_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
    {
        label: 'Delete all files',
        key: 'delete-all-files-link',
        stage: LG_RECORD_STAGE.DELETE_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
];
