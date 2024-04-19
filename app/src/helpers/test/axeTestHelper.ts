/* eslint-disable import/no-extraneous-dependencies */
import { configureAxe, JestAxeConfigureOptions } from 'jest-axe';
import 'jest-axe/extend-expect';

const axeConfigs: JestAxeConfigureOptions = {
    rules: {
        // disable landmark rules as we are testing components
        region: { enabled: false },
    },
};

// TODO: Remove this global suppress options once we complete Scenario 4 of PRMDR-809
const SUPPRESS_ACCESSIBILITY_TEST = false;
if (SUPPRESS_ACCESSIBILITY_TEST) {
    // eslint-disable-next-line no-console
    console.warn('Accessibility tests are turned off');
    // @ts-ignore
    axeConfigs['impactLevels'] = [null];
}

export const runAxeTest = configureAxe(axeConfigs);
