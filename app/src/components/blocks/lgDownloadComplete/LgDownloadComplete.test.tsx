import { useState } from 'react';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { PatientDetails } from '../../../types/generic/patientDetails';
import LgDownloadComplete, { Props } from './LgDownloadComplete';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

const mockPatient = buildPatientDetails();
describe('LgDownloadComplete', () => {
    it('renders the component', () => {
        renderComponent(mockPatient);

        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
        expect(screen.getByText('Documents from the Lloyd George record of:')).toBeInTheDocument();
        expect(
            screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: "Return to patient's available medical records" }),
        ).toBeInTheDocument();
    });

    it('updates the download stage view when return to medical records is clicked', async () => {
        renderComponent(mockPatient);

        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
        expect(screen.getByText('Documents from the Lloyd George record of:')).toBeInTheDocument();
        expect(
            screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
        ).toBeInTheDocument();

        const returnToRecordButton = screen.getByRole('button', {
            name: "Return to patient's available medical records",
        });
        expect(returnToRecordButton).toBeInTheDocument();
        expect(screen.getByTestId(LG_RECORD_STAGE.DOWNLOAD_ALL)).toBeInTheDocument();
        expect(screen.queryByTestId(LG_RECORD_STAGE.RECORD)).not.toBeInTheDocument();

        userEvent.click(returnToRecordButton);

        await waitFor(async () => {
            expect(screen.getByTestId(LG_RECORD_STAGE.RECORD)).toBeInTheDocument();
        });
        expect(screen.queryByTestId(LG_RECORD_STAGE.DOWNLOAD_ALL)).not.toBeInTheDocument();
    });
});

const TestApp = ({ patientDetails }: Omit<Props, 'setStage'>) => {
    const [stage, setStage] = useState(LG_RECORD_STAGE.DOWNLOAD_ALL);

    return <LgDownloadComplete patientDetails={patientDetails} setStage={setStage} stage={stage} />;
};

const renderComponent = (patientDetails: PatientDetails) => {
    render(<TestApp patientDetails={patientDetails} />);
};
