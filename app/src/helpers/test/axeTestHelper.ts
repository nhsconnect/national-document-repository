/* eslint-disable import/no-extraneous-dependencies */
import { configureAxe } from 'jest-axe';
import 'jest-axe/extend-expect';

const axeConfigs = {
    rules: {
        // disable landmark rules when testing components
        region: { enabled: false },
    },
};
const axeConfigsForLayout = { rules: {} };

const suppressRules = {
    // TODO: Remove the rule supress options to enable accessibility auto-test.
    list: { enabled: false },
    listitem: { enabled: false },
    region: { enabled: false },
    'nested-interactive': { enabled: false },
    'duplicate-id-active': { enabled: false },
    'duplicate-id': { enabled: false },
};

const SUPPRESS_ACCESSIBILITY_TEST = true;
if (SUPPRESS_ACCESSIBILITY_TEST) {
    Object.assign(axeConfigs.rules, suppressRules);
    Object.assign(axeConfigsForLayout.rules, suppressRules);
}

export const runAxeTest = configureAxe(axeConfigs);
export const runAxeTestForLayout = configureAxe(axeConfigsForLayout);
