import React from 'react';
import 'react-toggle/style.css';
import { isLocal } from '../../../helpers/utils/isLocal';
import {
    LocalFlags,
    useFeatureFlagsContext,
} from '../../../providers/featureFlagsProvider/FeatureFlagsProvider';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import TestToggle, { ToggleProps } from './TestToggle';

function TestPanel() {
    const [featureFlags, setFeatureFlags] = useFeatureFlagsContext();
    const { isBsol, recordUploaded, userRole } = featureFlags.mockLocal;

    const updateLocalFlag = (key: keyof LocalFlags, value: boolean | REPOSITORY_ROLE) => {
        setFeatureFlags({
            ...featureFlags,
            mockLocal: {
                ...featureFlags.mockLocal,
                [key]: value,
            },
        });
    };

    const roleToggles = {
        'gp-admin-toggle': {
            label: 'GP Admin',
            checked: userRole === REPOSITORY_ROLE.GP_ADMIN,
            onChange: () => {
                updateLocalFlag('userRole', REPOSITORY_ROLE.GP_ADMIN);
            },
        },
        'gp-clinical-toggle': {
            label: 'GP Clinical',
            checked: userRole === REPOSITORY_ROLE.GP_CLINICAL,
            onChange: () => {
                updateLocalFlag('userRole', REPOSITORY_ROLE.GP_CLINICAL);
            },
        },
        'pcse-toggle': {
            label: 'PCSE',
            checked: userRole === REPOSITORY_ROLE.PCSE,
            onChange: () => {
                updateLocalFlag('userRole', REPOSITORY_ROLE.PCSE);
            },
        },
    };

    const dataToggles = {
        'bsol-toggle': {
            label: 'User is BSOL',
            checked: !!isBsol,
            onChange: () => {
                updateLocalFlag('isBsol', !isBsol);
            },
        },
        'record-toggle': {
            label: 'Patient has a record',
            checked: !!recordUploaded,
            onChange: () => {
                updateLocalFlag('recordUploaded', !recordUploaded);
            },
        },
    };

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
                    <h3>Local mock</h3>
                    <p>
                        This section is only available when the environment is set to local, and
                        allows for navigating to areas of the app required for developing
                    </p>
                    <h4>Role</h4>
                    <div style={{ marginBottom: '32px' }}>
                        {Object.entries(roleToggles).map(([id, value]) => {
                            const toggleProps: ToggleProps = {
                                id,
                                ...value,
                            };
                            return <TestToggle key={id} {...toggleProps} />;
                        })}
                    </div>
                    <h4>Data</h4>
                    {Object.entries(dataToggles).map(([id, value]) => {
                        const toggleProps: ToggleProps = {
                            id,
                            ...value,
                        };
                        return <TestToggle key={id} {...toggleProps} />;
                    })}
                </div>
            )}
        </div>
    );
}

export default TestPanel;
