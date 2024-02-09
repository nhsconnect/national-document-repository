import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FeatureFlagsProvider, { FeatureFlags, useFeatureFlagsContext } from './FeatureFlagsProvider';
describe('SessionProvider', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('is able to set and retrieve auth data when user has logged in', async () => {
        renderFeatureFlagsProvider();
        expect(screen.getByText('testFeature - false')).toBeInTheDocument();
        act(() => {
            userEvent.click(screen.getByText('Flag On'));
        });

        expect(screen.getByText('testFeature - true')).toBeInTheDocument();
    });

    it('is able to delete auth data when user has logged out', async () => {
        renderFeatureFlagsProvider();
        expect(screen.getByText('testFeature - true')).toBeInTheDocument();
        act(() => {
            userEvent.click(screen.getByText('Flag Off'));
        });

        expect(screen.getByText('testFeature - false')).toBeInTheDocument();
    });
});

const TestApp = () => {
    const [featureFlags, setFeatureFlags] = useFeatureFlagsContext();
    const flagOn: FeatureFlags = {
        ...featureFlags,
        appConfig: {
            testFeature: true,
        },
    };
    const flagOff: FeatureFlags = {
        ...featureFlags,
        appConfig: {},
    };
    return (
        <>
            <div>
                <h1>Actions</h1>
                <div onClick={() => setFeatureFlags(flagOn)}>Flag On</div>
                <div onClick={() => setFeatureFlags(flagOff)}>Flag Off</div>
            </div>
            <div>
                <h1>Flags</h1>
                <span>testFeature - {`${!!featureFlags.appConfig.testFeature}`}</span>
            </div>
        </>
    );
};

const renderFeatureFlagsProvider = () => {
    render(
        <FeatureFlagsProvider>
            <TestApp />
        </FeatureFlagsProvider>,
    );
};
