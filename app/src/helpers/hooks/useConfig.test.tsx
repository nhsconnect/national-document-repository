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
    const config = useConfig();
    return <div>{`FLAG: ${!!config.featureFlags.testFeature1}`.normalize()}</div>;
};

const renderHook = (config?: GlobalConfig) => {
    return render(
        <ConfigProvider configOverride={config}>
            <TestApp />
        </ConfigProvider>,
    );
};
