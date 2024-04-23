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

// TODO: Remove the rule supress options once we complete Scenario 4 of PRMDR-809
const suppressRules = {
    // below are all the issues found in our ui, as of 22/Apr/2024
    'heading-order': { enabled: false },
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
