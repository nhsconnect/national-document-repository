import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import { PatientDetails } from '../../../types/generic/patientDetails';
import LgDownloadComplete, { Props } from './LloydGeorgeDownloadComplete';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { act } from 'react-dom/test-utils';

const mockSetStage = jest.fn();
const mockPatient = buildPatientDetails();
describe('LloydGeorgeDownloadComplete', () => {
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

        act(() => {
            userEvent.click(returnToRecordButton);
        });

        await waitFor(async () => {
            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
        });
    });
});

const TestApp = ({ patientDetails }: Omit<Props, 'setStage'>) => {
    return <LgDownloadComplete patientDetails={patientDetails} setStage={mockSetStage} />;
};

const renderComponent = (patientDetails: PatientDetails) => {
    render(<TestApp patientDetails={patientDetails} />);
};
