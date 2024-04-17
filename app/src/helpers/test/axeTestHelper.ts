/* eslint-disable import/no-extraneous-dependencies */
import { configureAxe } from 'jest-axe';
import 'jest-axe/extend-expect';

// to allow setting global ignore rule option if needed.
export const runAxeTest = configureAxe({
    rules: {
        // disable landmark rules as we are testing components.
        region: { enabled: false },
    },
});
