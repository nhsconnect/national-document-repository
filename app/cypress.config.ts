import { defineConfig } from 'cypress';
import * as dotenv from 'dotenv';

dotenv.config();
export default defineConfig({
    e2e: {
        setupNodeEvents(on, config) {
            // implement node event listeners here
        },
        downloadsFolder: 'cypress/downloads',
        trashAssetsBeforeRuns: true,
        baseUrl: process.env.CYPRESS_BASE_URL,
    },
    env: {
        USERNAME: process.env.CYPRESS_USERNAME,
        PASSWORD: process.env.CYPRESS_PASSWORD,
        WORKSPACE: process.env.CYPRESS_WORKSPACE ?? 'local',
        AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY,
        AWS_REGION: process.env.AWS_REGION,
        AWS_SESSION_TOKEN: process.env.AWS_SESSION_TOKEN,
    },
    component: {
        devServer: {
            framework: 'create-react-app',
            bundler: 'webpack',
        },
    },
    reporter: 'mochawesome',
    reporterOptions: {
        reportDir: 'cypress/results',
        overwrite: false,
        html: false,
        json: true,
    },
});
