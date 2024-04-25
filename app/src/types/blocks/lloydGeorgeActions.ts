import { REPOSITORY_ROLE } from '../generic/authRole';
import { routes } from '../generic/routes';
import { LG_RECORD_STAGE } from './lloydGeorgeStages';

export enum RECORD_ACTION {
    UPLOAD = 0,
    DOWNLOAD = 1,
}

export type PdfActionLink = {
    label: string;
    key: string;
    stage?: LG_RECORD_STAGE;
    href?: routes;
    type: RECORD_ACTION;
    unauthorised?: Array<REPOSITORY_ROLE>;
};

export const lloydGeorgeRecordLinks: Array<PdfActionLink> = [
    {
        label: 'Upload files',
        key: 'upload-files-link',
        type: RECORD_ACTION.UPLOAD,
        href: routes.LLOYD_GEORGE_UPLOAD,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
    {
        label: 'Remove a selection of files',
        key: 'delete-file-link',
        type: RECORD_ACTION.DOWNLOAD,
        stage: LG_RECORD_STAGE.DELETE_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
    {
        label: 'Remove all files',
        key: 'delete-all-files-link',
        type: RECORD_ACTION.DOWNLOAD,
        stage: LG_RECORD_STAGE.DELETE_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
    {
        label: 'Download all files',
        key: 'download-all-files-link',
        type: RECORD_ACTION.DOWNLOAD,
        stage: LG_RECORD_STAGE.DOWNLOAD_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
];
