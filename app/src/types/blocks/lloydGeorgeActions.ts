import { REPOSITORY_ROLE } from '../generic/authRole';
import { routes } from '../generic/routes';
import { LG_RECORD_STAGE } from './lloydGeorgeStages';

export enum RECORD_ACTION {
    UPDATE = 0,
    DOWNLOAD = 1,
}

export type PdfActionLink = {
    label: string;
    key: string;
    stage?: LG_RECORD_STAGE;
    href?: routes;
    onClick?: () => void;
    type: RECORD_ACTION;
    unauthorised?: Array<REPOSITORY_ROLE>;
    showIfRecordInRepo: boolean;
};

export const lloydGeorgeRecordLinks: Array<PdfActionLink> = [
    {
        label: 'Remove files',
        key: 'delete-all-files-link',
        type: RECORD_ACTION.UPDATE,
        stage: LG_RECORD_STAGE.DELETE_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInRepo: true,
    },
    {
        label: 'Download files',
        key: 'download-all-files-link',
        type: RECORD_ACTION.DOWNLOAD,
        stage: LG_RECORD_STAGE.DOWNLOAD_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInRepo: true,
    },
];
type Args = {
    role: REPOSITORY_ROLE | null;
    hasRecordInRepo: boolean;
    inputLinks?: Array<PdfActionLink>;
};

export function getAllowedRecordLinks({
    role,
    hasRecordInRepo,
    inputLinks,
}: Args): Array<PdfActionLink> {
    if (!inputLinks) {
        inputLinks = lloydGeorgeRecordLinks;
    }

    const allowedLinks = inputLinks.filter((link) => {
        if (!role || link.unauthorised?.includes(role)) {
            return false;
        }
        return hasRecordInRepo === link.showIfRecordInRepo;
    });
    return allowedLinks;
}

type ArgsNonBsol = {
    role: REPOSITORY_ROLE | null;
    hasRecordInRepo: boolean;
    downloadAndRemoveOnClick: () => void;
};

export function getAllowedRecordLinksForNonBSOL({
    role,
    hasRecordInRepo,
    downloadAndRemoveOnClick,
}: ArgsNonBsol): Array<PdfActionLink> {
    const lloydGeorgeRecordLinksNonBSOL: Array<PdfActionLink> = [
        {
            label: 'Download and remove files',
            key: 'download-and-delete-all-files-link',
            type: RECORD_ACTION.DOWNLOAD,
            unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
            showIfRecordInRepo: true,
            onClick: downloadAndRemoveOnClick,
        },
    ];
    const allowedLinks = getAllowedRecordLinks({
        role,
        hasRecordInRepo,
        inputLinks: lloydGeorgeRecordLinksNonBSOL,
    });

    return allowedLinks;
}
