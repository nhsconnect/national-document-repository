import React from 'react';
import Toggle from 'react-toggle';
import 'react-toggle/style.css';
import { isLocal } from '../../../helpers/utils/isLocal';
import { useFeatureFlagsContext } from '../../../providers/featureFlagsProvider/FeatureFlagsProvider';

function TestPanel() {
    const [featureFlags, setFeatureFlags] = useFeatureFlagsContext();
    const { isBsol, recordUploaded } = featureFlags.mockLocal;

    return (
        <div>
            <br />
            <br />
            <br />
            <h2>Test Panel</h2>
            <p>
                This section should only be displayed on a test/dev environment and should be used
                for displaying test configurations
            </p>
            <p> API endpoint: {process.env.REACT_APP_DOC_STORE_API_ENDPOINT}</p>
            <p> Image Version: {process.env.REACT_APP_IMAGE_VERSION}</p>

            {isLocal && (
                <div>
                    <h3>Local mocks</h3>
                    <div
                        style={{
                            display: 'flex',
                            flexFlow: 'row nowrap',
                            alignItems: 'center',
                            marginBottom: '12px',
                        }}
                    >
                        <Toggle
                            id="mock-bsol-toggle"
                            defaultChecked={!!isBsol}
                            onChange={() => {
                                setFeatureFlags({
                                    ...featureFlags,
                                    mockLocal: {
                                        ...featureFlags.mockLocal,
                                        isBsol: !isBsol,
                                    },
                                });
                            }}
                        />
                        <label htmlFor="mock-bsol-toggle" style={{ marginLeft: '6px' }}>
                            <p style={{ marginBottom: '0px' }}>User is BSOL</p>
                        </label>
                    </div>

                    <div
                        style={{
                            display: 'flex',
                            flexFlow: 'row nowrap',
                            alignItems: 'center',
                            marginBottom: '12px',
                        }}
                    >
                        <Toggle
                            id="mock-record-toggle"
                            defaultChecked={!!recordUploaded}
                            onChange={() => {
                                setFeatureFlags({
                                    ...featureFlags,
                                    mockLocal: {
                                        ...featureFlags.mockLocal,
                                        recordUploaded: !recordUploaded,
                                    },
                                });
                            }}
                        />
                        <label htmlFor="mock-record-toggle" style={{ marginLeft: '6px' }}>
                            <p style={{ marginBottom: '0px' }}>Patient has a record</p>
                        </label>
                    </div>
                </div>
            )}
        </div>
    );
}

export default TestPanel;
