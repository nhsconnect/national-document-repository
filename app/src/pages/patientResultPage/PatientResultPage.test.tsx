import { render, screen } from '@testing-library/react';
import PatientResultPage from './PatientResultPage';
import { USER_ROLE } from '../../types/generic/roles';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import { PatientDetails } from '../../types/generic/patientDetails';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';

describe('PatientResultPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders component', () => {
        renderPatientResultPage();

        expect(screen.getByText('Verify patient details')).toBeInTheDocument();
    });

    it('renders the patient details page when patient data is found', async () => {
        const nhsNumber = '9000000000';
        const familyName = 'Smith';
        const patientDetails = buildPatientDetails({ familyName, nhsNumber });

        renderPatientResultPage(patientDetails);

        expect(screen.getByRole('heading', { name: 'Verify patient details' })).toBeInTheDocument();
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

        expect(screen.getByRole('heading', { name: 'Verify patient details' })).toBeInTheDocument();
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

        expect(screen.getByRole('heading', { name: 'Verify patient details' })).toBeInTheDocument();
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

        expect(screen.getByRole('heading', { name: 'Verify patient details' })).toBeInTheDocument();
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

        expect(screen.getByRole('heading', { name: 'Verify patient details' })).toBeInTheDocument();
        expect(
            screen.getByText(
                'Certain details about this patient cannot be displayed without the necessary access.',
            ),
        ).toBeInTheDocument();
    });
});

const renderPatientResultPage = (
    patientOverride: Partial<PatientDetails> = {},
    role: USER_ROLE = USER_ROLE.PCSE,
) => {
    const patient: PatientDetails = {
        ...buildPatientDetails(),
        ...patientOverride,
    };
    const history = createMemoryHistory({
        initialEntries: ['/', '/example'],
        initialIndex: 1,
    });

    render(
        <ReactRouter.Router navigator={history} location={'/example'}>
            <PatientDetailsProvider patientDetails={patient}>
                <PatientResultPage role={role} />
            </PatientDetailsProvider>
        </ReactRouter.Router>,
    );
};
