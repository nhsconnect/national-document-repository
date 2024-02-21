import { render, screen } from '@testing-library/react';
import useFeatureFlags from './useFeatureFlags';
import FeatureFlagsProvider, {
    FeatureFlags,
} from '../../providers/featureFlagsProvider/FeatureFlagsProvider';
import { defaultFeatureFlags } from '../requests/getFeatureFlags';

let defaultTestFeatureFlags = defaultFeatureFlags

describe('useFeatureFlags', () => {
    beforeEach(() => {
        sessionStorage.setItem('FeatureFlags', '');
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    // it('returns true when feature flag in context', () => {
    //     let testFlags = defaultTestFeatureFlags
    //     testFlags.testFeature1 = true

    //     const appConfig: Partial<FeatureFlags> = { appConfig: { ...testFlags } };
    //     renderHook(appConfig);
    //     expect(screen.getByText(`FLAG: true`)).toBeInTheDocument();
    // });

    // it('returns false when there is no feature flag in context', () => {
    //     let testFlags = defaultTestFeatureFlags
    //     testFlags.testFeature1 = true

    //     const appConfig: Partial<FeatureFlags> = { appConfig: {} };
    //     renderHook(appConfig);
    //     expect(screen.getByText(`FLAG: false`)).toBeInTheDocument();
    // });
});

const TestApp = () => {
    const featureFlags = useFeatureFlags();
    return <div>{`FLAG: ${!!featureFlags.appConfig.testFeature1}`.normalize()}</div>;
};

const renderHook = (featureFlags?: Partial<FeatureFlags>) => {
    return render(
        <FeatureFlagsProvider featureFlagsOverride={featureFlags}>
            <TestApp />
        </FeatureFlagsProvider>,
    );
};
