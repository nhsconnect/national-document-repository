import { render, screen } from '@testing-library/react';
import LloydGeorgeRecordPage from './LloydGeorgeRecordPage';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { buildPatientDetails } from '../../helpers/test/testBuilders';

const mockPatientDetails = buildPatientDetails();

describe('LloydGeorgeRecordPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders patient details', () => {
        const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;

        renderPage();

        expect(screen.getByText(patientName)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
    });
});

const renderPage = () => {
    render(
        <PatientDetailsProvider patientDetails={mockPatientDetails}>
            <LloydGeorgeRecordPage />
        </PatientDetailsProvider>,
    );
};
