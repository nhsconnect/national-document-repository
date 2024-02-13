import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { Dispatch, ReactNode, SetStateAction } from 'react';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { isLocal } from '../../helpers/utils/isLocal';

type SetFeatureFlagsOverride = (featureFlags: FeatureFlags) => void;

type Props = {
    children: ReactNode;
    featureFlagsOverride?: Partial<FeatureFlags>;
    setFeatureFlagsOverride?: SetFeatureFlagsOverride;
};

export type LocalFlags = {
    isBsol?: boolean;
    recordUploaded?: boolean;
    userRole?: REPOSITORY_ROLE;
};

export type FeatureFlags = {
    appConfig: {
        testFeature?: true;
        testRoute?: true;
    };
    mockLocal: LocalFlags;
};

export type TFeatureFlagsContext = [
    FeatureFlags,
    Dispatch<SetStateAction<FeatureFlags>> | SetFeatureFlagsOverride,
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
    const flags: FeatureFlags = storedFlags ? JSON.parse(storedFlags) : emptyFlags;
    const [featureFlags, setFeatureFlags] = useState<FeatureFlags>({
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
