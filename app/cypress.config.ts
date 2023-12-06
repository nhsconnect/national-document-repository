import { defineConfig } from 'cypress';

export default defineConfig({
    e2e: {
        setupNodeEvents(on, config) {
            // implement node event listeners here
        },
        downloadsFolder: 'cypress/downloads',
        trashAssetsBeforeRuns: true,
        baseUrl: process.env.CYPRESS_BASE_URL,
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
