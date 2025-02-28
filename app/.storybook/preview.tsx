import React from 'react';
import type { Preview } from '@storybook/react';
import '../src/styles/App.scss';
import { MemoryRouter } from 'react-router-dom';
import PatientDetailsProvider from '../src/providers/patientProvider/PatientProvider';

import { buildPatientDetails } from '../src/helpers/test/testBuilders';
const preview: Preview = {
    parameters: {
        actions: { argTypesRegex: '^on[A-Z].*' },
        controls: {
            matchers: {
                color: /(background|color)$/i,
                date: /Date$/,
            },
        },
    },
    decorators: [
        (Story) => (
            <PatientDetailsProvider patientDetails={{ ...buildPatientDetails() }}>
                <MemoryRouter initialEntries={['/']}>
                    <div className="nhsuk-width-container preview">
                        <main
                            className="nhsuk-main-wrapper app-homepage"
                            id="maincontent"
                            role="main"
                        >
                            <section className="app-homepage-content">
                                <div>
                                    <Story />
                                </div>
                            </section>
                        </main>
                    </div>
                </MemoryRouter>
            </PatientDetailsProvider>
        ),
    ],
};
export default preview;
