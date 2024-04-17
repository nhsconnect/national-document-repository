import { REPOSITORY_ROLE } from '../generic/authRole';
import { routes } from '../generic/routes';
import { LG_RECORD_STAGE } from './lloydGeorgeStages';

type PdfActionLink = {
    label: string;
    key: string;
    stage?: LG_RECORD_STAGE;
    href?: routes;
    unauthorised?: Array<REPOSITORY_ROLE>;
};

export const actionLinks: Array<PdfActionLink> = [
    {
        label: 'Upload files',
        key: 'upload-files-link',
        href: routes.LLOYD_GEORGE_UPLOAD,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
    {
        label: 'Remove a selection of files',
        key: 'delete-file-link',
        stage: LG_RECORD_STAGE.DELETE_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
    {
        label: 'Remove all files',
        key: 'delete-all-files-link',
        stage: LG_RECORD_STAGE.DELETE_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
    {
        label: 'Download all files',
        key: 'download-all-files-link',
        stage: LG_RECORD_STAGE.DOWNLOAD_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
    },
];
