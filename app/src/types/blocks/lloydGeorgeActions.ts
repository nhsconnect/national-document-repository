import { REPOSITORY_ROLE } from '../generic/authRole';
import { routeChildren } from '../generic/routes';
import { LG_RECORD_STAGE } from './lloydGeorgeStages';

export enum RECORD_ACTION {
    UPDATE = 0,
    DOWNLOAD = 1,
}

export type LGRecordActionLink = {
    label: string;
    key: string;
    stage?: LG_RECORD_STAGE;
    href?: unknown;
    onClick?: () => void;
    type: RECORD_ACTION;
    unauthorised?: Array<REPOSITORY_ROLE>;
    showIfRecordInStorage: boolean;
};

export const lloydGeorgeRecordLinksInBSOL: Array<LGRecordActionLink> = [
    {
        label: 'Remove files',
        key: 'delete-all-files-link',
        type: RECORD_ACTION.UPDATE,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInRepo: true,
        href: routeChildren.LLOYD_GEORGE_DELETE,
        showIfRecordInStorage: true,

    },
    {
        label: 'Download files',
        key: 'download-all-files-link',
        type: RECORD_ACTION.DOWNLOAD,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInRepo: true,
        href: routeChildren.LLOYD_GEORGE_DOWNLOAD,
        showIfRecordInStorage: true,
    },
];

type Args = {
    role: REPOSITORY_ROLE | null;
    hasRecordInStorage: boolean;
    inputLinks: Array<LGRecordActionLink>;
};

export function getRecordActionLinksAllowedForRole({
    role,
    hasRecordInStorage,
    inputLinks,
}: Args): Array<LGRecordActionLink> {
    const allowedLinks = inputLinks.filter((link) => {
        if (!role || link.unauthorised?.includes(role)) {
            return false;
        }
        return hasRecordInStorage === link.showIfRecordInStorage;
    });
    return allowedLinks;
}

type ArgsInBsol = Omit<Args, 'inputLinks'>;

export function getBSOLUserRecordActionLinks({
    role,
    hasRecordInStorage,
}: ArgsInBsol): Array<LGRecordActionLink> {
    const allowedLinks = getRecordActionLinksAllowedForRole({
        role,
        hasRecordInStorage,
        inputLinks: lloydGeorgeRecordLinksInBSOL,
    });

    return allowedLinks;
}

type ArgsNonBsol = {
    onClickFunctionForDownloadAndRemove: () => void;
} & Omit<Args, 'inputLinks'>;

export function getNonBSOLUserRecordActionLinks({
    role,
    hasRecordInStorage,
    onClickFunctionForDownloadAndRemove,
}: ArgsNonBsol): Array<LGRecordActionLink> {
    const lloydGeorgeRecordLinksNonBSOL: Array<LGRecordActionLink> = [
        {
            label: 'Download and remove files',
            key: 'download-and-remove-record-btn',
            type: RECORD_ACTION.DOWNLOAD,
            unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
            showIfRecordInStorage: true,
            onClick: onClickFunctionForDownloadAndRemove,
        },
    ];
    const allowedLinks = getRecordActionLinksAllowedForRole({
        role,
        hasRecordInStorage,
        inputLinks: lloydGeorgeRecordLinksNonBSOL,
    });

    return allowedLinks;
}
