import { useFeatureFlagsContext } from '../../providers/featureFlagsProvider/FeatureFlagsProvider';

function useFeatureFlags() {
    const [featureFlags] = useFeatureFlagsContext();
    return featureFlags;
}

export default useFeatureFlags;
