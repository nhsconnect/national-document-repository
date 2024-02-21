import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { Dispatch, ReactNode, SetStateAction } from 'react';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { isLocal } from '../../helpers/utils/isLocal';
import { FeatureFlags } from '../../types/generic/featureFlags';

type SetFeatureFlagsOverride = (featureFlags: GlobalConfig) => void;

type Props = {
    children: ReactNode;
    featureFlagsOverride?: Partial<GlobalConfig>;
    setFeatureFlagsOverride?: SetFeatureFlagsOverride;
};

export type LocalFlags = {
    isBsol?: boolean;
    recordUploaded?: boolean;
    userRole?: REPOSITORY_ROLE;
};

export type GlobalConfig = {
    appConfig: FeatureFlags;
    mockLocal: LocalFlags;
};

export type TFeatureFlagsContext = [
    GlobalConfig,
    Dispatch<SetStateAction<GlobalConfig>> | SetFeatureFlagsOverride,
];

const FeatureFlagsContext = createContext<TFeatureFlagsContext | null>(null);
const FeatureFlagsProvider = ({
    children,
    featureFlagsOverride,
    setFeatureFlagsOverride,
}: Props) => {
    const emptyFlags = useMemo(
        () => ({
            appConfig: { ...featureFlagsOverride?.appConfig },
            mockLocal: {
                ...featureFlagsOverride?.mockLocal,
            },
        }),
        [featureFlagsOverride],
    );
    const localDefaults = isLocal
        ? {
              isBsol: true,
              recordUploaded: true,
              userRole: REPOSITORY_ROLE.GP_ADMIN,
              ...featureFlagsOverride?.mockLocal,
          }
        : null;
    const storedFlags = sessionStorage.getItem('FeatureFlags');
    const flags: GlobalConfig = storedFlags ? JSON.parse(storedFlags) : emptyFlags;
    const [featureFlags, setFeatureFlags] = useState<GlobalConfig>({
        mockLocal: {
            ...localDefaults,
            ...flags.mockLocal,
            ...featureFlagsOverride?.mockLocal,
        },
        appConfig: {
            ...flags.appConfig,
            ...featureFlagsOverride?.appConfig,
        },
    });

    useEffect(() => {
        sessionStorage.setItem('FeatureFlags', JSON.stringify(featureFlags) ?? emptyFlags);
    }, [featureFlags, emptyFlags]);

    return (
        <FeatureFlagsContext.Provider
            value={[featureFlags, setFeatureFlagsOverride ?? setFeatureFlags]}
        >
            {children}
        </FeatureFlagsContext.Provider>
    );
};

export default FeatureFlagsProvider;
export const useFeatureFlagsContext = () => useContext(FeatureFlagsContext) as TFeatureFlagsContext;
