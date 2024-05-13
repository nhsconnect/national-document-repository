import { REPOSITORY_ROLE } from '../generic/authRole';
import { routeChildren } from '../generic/routes';
import { LG_RECORD_STAGE } from './lloydGeorgeStages';

export enum RECORD_ACTION {
    UPDATE = 0,
    DOWNLOAD = 1,
}

export type PdfActionLink = {
    label: string;
    key: string;
    stage?: LG_RECORD_STAGE;
    href?: unknown;
    type: RECORD_ACTION;
    unauthorised?: Array<REPOSITORY_ROLE>;
    showIfRecordInRepo: boolean;
};

export const lloydGeorgeRecordLinks: Array<PdfActionLink> = [
    {
        label: 'Remove files',
        key: 'delete-all-files-link',
        type: RECORD_ACTION.UPDATE,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInRepo: true,
        href: routeChildren.LLOYD_GEORGE_DELETE,
    },
    {
        label: 'Download files',
        key: 'download-all-files-link',
        type: RECORD_ACTION.DOWNLOAD,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInRepo: true,
        href: routeChildren.LLOYD_GEORGE_DOWNLOAD,
    },
];

type Args = {
    role: REPOSITORY_ROLE | null;
    hasRecordInRepo: boolean;
};

export function getRecordActionLinksAllowedForRole({
    role,
    hasRecordInRepo,
}: Args): Array<PdfActionLink> {
    const allowedLinks = lloydGeorgeRecordLinks.filter((link) => {
        if (!role || link.unauthorised?.includes(role)) {
            return false;
        }
        return hasRecordInRepo === link.showIfRecordInRepo;
    });
    return allowedLinks;
}
