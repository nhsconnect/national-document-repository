import { render, screen } from '@testing-library/react';
import useFeatureFlags from './useFeatureFlags';
import FeatureFlagsProvider, {
    GlobalConfig,
} from '../../providers/featureFlagsProvider/FeatureFlagsProvider';
import { defaultFeatureFlags } from '../requests/getFeatureFlags';

describe('useFeatureFlags', () => {
    beforeEach(() => {
        sessionStorage.setItem('FeatureFlags', '');
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('returns true when feature flag in context', () => {
        const appConfig: GlobalConfig = {
            appConfig: { ...defaultFeatureFlags, testFeature1: true },
            mockLocal: {},
        };
        renderHook(appConfig);
        expect(screen.getByText(`FLAG: true`)).toBeInTheDocument();
    });

    it('returns false when there is no feature flag in context', () => {
        const appConfig: GlobalConfig = {
            appConfig: { ...defaultFeatureFlags, testFeature1: false },
            mockLocal: {},
        };
        renderHook(appConfig);
        expect(screen.getByText(`FLAG: false`)).toBeInTheDocument();
    });
});

const TestApp = () => {
    const featureFlags = useFeatureFlags();
    return <div>{`FLAG: ${!!featureFlags.appConfig.testFeature1}`.normalize()}</div>;
};

const renderHook = (featureFlags?: GlobalConfig) => {
    return render(
        <FeatureFlagsProvider featureFlagsOverride={featureFlags}>
            <TestApp />
        </FeatureFlagsProvider>,
    );
};
