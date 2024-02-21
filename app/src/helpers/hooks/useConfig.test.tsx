import { render, screen } from '@testing-library/react';
import useConfig from './useConfig';
import ConfigProvider, { GlobalConfig } from '../../providers/configProvider/ConfigProvider';
import { defaultFeatureFlags } from '../requests/getFeatureFlags';

describe('useConfig', () => {
    beforeEach(() => {
        sessionStorage.setItem('FeatureFlags', '');
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('returns true when feature flag in context', () => {
        const config: GlobalConfig = {
            featureFlags: { ...defaultFeatureFlags, testFeature1: true },
            mockLocal: {},
        };
        renderHook(config);
        expect(screen.getByText(`FLAG: true`)).toBeInTheDocument();
    });

    it('returns false when there is no feature flag in context', () => {
        const config: GlobalConfig = {
            featureFlags: { ...defaultFeatureFlags, testFeature1: false },
            mockLocal: {},
        };
        renderHook(config);
        expect(screen.getByText(`FLAG: false`)).toBeInTheDocument();
    });
});

const TestApp = () => {
    const featureFlags = useConfig();
    return <div>{`FLAG: ${!!featureFlags.featureFlags.testFeature1}`.normalize()}</div>;
};

const renderHook = (featureFlags?: GlobalConfig) => {
    return render(
        <ConfigProvider configOverride={featureFlags}>
            <TestApp />
        </ConfigProvider>,
    );
};
