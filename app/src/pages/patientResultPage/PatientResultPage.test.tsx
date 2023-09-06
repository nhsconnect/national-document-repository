import { render, screen, waitFor } from '@testing-library/react';
import PatientResultPage from './PatientResultPage';
import { USER_ROLE } from '../../types/generic/roles';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import { PatientDetails } from '../../types/generic/patientDetails';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import userEvent from '@testing-library/user-event';
import { routes } from '../../types/generic/routes';

describe('PatientResultPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('displays component', () => {
            renderPatientResultPage();

            expect(screen.getByText('Verify patient details')).toBeInTheDocument();
        });

        it('displays the patient details page when patient data is found', async () => {
            const nhsNumber = '9000000000';
            const familyName = 'Smith';
            const patientDetails = buildPatientDetails({ familyName, nhsNumber });

            renderPatientResultPage(patientDetails);

            expect(
                screen.getByRole('heading', { name: 'Verify patient details' }),
            ).toBeInTheDocument();
            expect(screen.getByText(familyName)).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Accept details are correct' }),
            ).toBeInTheDocument();
            expect(screen.getByText(/If patient details are incorrect/)).toBeInTheDocument();

            const nationalServiceDeskLink = screen.getByRole('link', {
                name: /National Service Desk/,
            });

            expect(nationalServiceDeskLink).toHaveAttribute(
                'href',
                'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
            );
            expect(nationalServiceDeskLink).toHaveAttribute('target', '_blank');
        });

        it('displays text specific to upload path if user has selected upload', async () => {
            const nhsNumber = '9000000000';
            const patientDetails = buildPatientDetails({ nhsNumber });
            const uploadRole = USER_ROLE.GP;

            renderPatientResultPage(patientDetails, uploadRole);

            expect(
                screen.getByRole('heading', { name: 'Verify patient details' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(
                    'Ensure these patient details match the electronic health records and attachments you are about to upload.',
                ),
            ).toBeInTheDocument();
        });

        it("doesn't display text specific to upload path if user has selected download", async () => {
            const nhsNumber = '9000000000';
            const patientDetails = buildPatientDetails({ nhsNumber });
            const downloadRole = USER_ROLE.PCSE;
            renderPatientResultPage(patientDetails, downloadRole);

            expect(
                screen.getByRole('heading', { name: 'Verify patient details' }),
            ).toBeInTheDocument();
            expect(
                screen.queryByText(
                    'Ensure these patient details match the electronic health records and attachments you are about to upload.',
                ),
            ).not.toBeInTheDocument();
        });

        it('displays a message when NHS number is superseded', async () => {
            const nhsNumber = '9000000012';
            const patientDetails = buildPatientDetails({ superseded: true, nhsNumber });

            renderPatientResultPage(patientDetails);

            expect(
                screen.getByRole('heading', { name: 'Verify patient details' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText('The NHS number for this patient has changed.'),
            ).toBeInTheDocument();
        });

        it('displays a message when patient is sensitive', async () => {
            const nhsNumber = '9124038456';
            const patientDetails = buildPatientDetails({
                nhsNumber,
                postalCode: null,
                restricted: true,
            });

            renderPatientResultPage(patientDetails);

            expect(
                screen.getByRole('heading', { name: 'Verify patient details' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(
                    'Certain details about this patient cannot be displayed without the necessary access.',
                ),
            ).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates to upload page when user has verified upload patient', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });

            const uploadRole = USER_ROLE.GP;

            renderPatientResultPage({}, uploadRole, history);
            expect(history.location.pathname).toBe('/example');

            userEvent.click(screen.getByRole('button', { name: 'Accept details are correct' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.UPLOAD_DOCUMENTS);
            });
        });
        it('navigates to download page when user has verified download patient', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });

            const downloadRole = USER_ROLE.PCSE;

            renderPatientResultPage({}, downloadRole, history);
            expect(history.location.pathname).toBe('/example');

            userEvent.click(screen.getByRole('button', { name: 'Accept details are correct' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.DOWNLOAD_DOCUMENTS);
            });
        });
    });
});

const homeRoute = '/example';
const renderPatientResultPage = (
    patientOverride: Partial<PatientDetails> = {},
    role: USER_ROLE = USER_ROLE.PCSE,
    history = createMemoryHistory({
        initialEntries: [homeRoute],
        initialIndex: 1,
    }),
) => {
    const patient: PatientDetails = {
        ...buildPatientDetails(),
        ...patientOverride,
    };

    render(
        <ReactRouter.Router navigator={history} location={homeRoute}>
            <PatientDetailsProvider patientDetails={patient}>
                <PatientResultPage role={role} />
            </PatientDetailsProvider>
        </ReactRouter.Router>,
    );
};
