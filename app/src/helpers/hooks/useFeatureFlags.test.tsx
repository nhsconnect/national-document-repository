import { render, screen } from '@testing-library/react';
import useFeatureFlags from './useFeatureFlags';
import FeatureFlagsProvider, {
    FeatureFlags,
} from '../../providers/featureFlagsProvider/FeatureFlagsProvider';

describe('useFeatureFlags', () => {
    beforeEach(() => {
        sessionStorage.setItem('FeatureFlags', '');
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('returns true when feature flag in context', () => {
        const appConfig: Partial<FeatureFlags> = { appConfig: { testFeature: true } };
        renderHook(appConfig);
        expect(screen.getByText(`FLAG: true`)).toBeInTheDocument();
    });

    it('returns false when there is no feature flag in context', () => {
        const appConfig: Partial<FeatureFlags> = { appConfig: {} };
        renderHook(appConfig);
        expect(screen.getByText(`FLAG: false`)).toBeInTheDocument();
    });
});

const TestApp = () => {
    const featureFlags = useFeatureFlags();
    return <div>{`FLAG: ${!!featureFlags.appConfig.testFeature}`.normalize()}</div>;
};

const renderHook = (featureFlags?: Partial<FeatureFlags>) => {
    return render(
        <FeatureFlagsProvider featureFlagsOverride={featureFlags}>
            <TestApp />
        </FeatureFlagsProvider>,
    );
};
