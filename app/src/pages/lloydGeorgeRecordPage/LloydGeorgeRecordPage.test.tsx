import { render, screen } from '@testing-library/react';
import LloydGeorgeRecordPage from './LloydGeorgeRecordPage';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { buildPatientDetails } from '../../helpers/test/testBuilders';

jest.mock('react-router');
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

    it('renders LG card', () => {
        renderPage();

        expect(screen.getByText('Lloyd George Record')).toBeInTheDocument();
    });

    xit('renders correct text in LG card if there is no LG pdf', () => {
        renderPage();

        expect(screen.getByText('Lloyd George Record')).toBeInTheDocument();
        expect(screen.getByText('No documents are available')).toBeInTheDocument();
    });
});

const renderPage = () => {
    render(
        <PatientDetailsProvider patientDetails={mockPatientDetails}>
            <LloydGeorgeRecordPage />
        </PatientDetailsProvider>,
    );
};
