import { render, screen, waitFor } from '@testing-library/react';
import { buildLgSearchResult, buildPatientDetails } from '../../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import LgRecordStage, { Props } from './LgRecordStage';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import { useState } from 'react';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
const mockPdf = buildLgSearchResult();
describe('LgRecordStage', () => {
    const mockPdf = buildLgSearchResult();
    const mockPatientDetails = buildPatientDetails();
    // it('renders lg record stage component', () => {

    // })
    it("renders 'full screen' mode correctly", async () => {
        const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
        const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));

        renderComponent();

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });

        userEvent.click(screen.getByText('View in full screen'));

        await waitFor(() => {
            expect(screen.queryByText('Lloyd George record')).not.toBeInTheDocument();
        });
        expect(screen.getByText('Go back')).toBeInTheDocument();
        expect(screen.getByText(patientName)).toBeInTheDocument();
        expect(screen.getByText(`Date of birth: ${dob}`)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
    });
});
const TestApp = (props: Omit<Props, 'setStage'>) => {
    const [, setStage] = useState(LG_RECORD_STAGE.RECORD);
    return <LgRecordStage {...props} setStage={setStage} />;
};

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage'> = {
        patientDetails: buildPatientDetails(),
        downloadStage: DOWNLOAD_STAGE.SUCCEEDED,
        lloydGeorgeUrl: mockPdf.presign_url,
        lastUpdated: mockPdf.last_updated,
        numberOfFiles: mockPdf.number_of_files,
        totalFileSizeInByte: mockPdf.total_file_size_in_byte,

        ...propsOverride,
    };
    render(<TestApp {...props} />);
};
