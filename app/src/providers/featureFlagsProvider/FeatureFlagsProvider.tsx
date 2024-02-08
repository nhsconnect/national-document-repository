import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { Dispatch, ReactNode, SetStateAction } from 'react';

type SetFeatureFlagsOverride = (featureFlags: FeatureFlags) => void;

type Props = {
    children: ReactNode;
    featureFlagsOverride?: Partial<FeatureFlags>;
    setFeatureFlagsOverride?: SetFeatureFlagsOverride;
};
export type FeatureFlags = {
    appConfig: {
        testFeature?: true;
        testRoute?: true;
    };
    mockLocal: {
        isBsol?: boolean;
        recordUploaded?: boolean;
    };
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
    debugger;
    const storedFlags = sessionStorage.getItem('FeatureFlags');
    const flags: FeatureFlags = storedFlags ? JSON.parse(storedFlags) : emptyFlags;
    const [featureFlags, setFeatureFlags] = useState<FeatureFlags>({
        mockLocal: {
            isBsol: true,
            recordUploaded: true,
            ...featureFlagsOverride?.mockLocal,
        },
        appConfig: {
            testFeature: true,
            // ...flags.appConfig,
            // ...featureFlagsOverride?.appConfig,
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
