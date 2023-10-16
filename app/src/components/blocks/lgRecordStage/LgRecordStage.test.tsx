import { render, screen, waitFor } from '@testing-library/react';
import { buildLgSearchResult, buildPatientDetails } from '../../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import LgRecordStage, { Props } from './LgRecordStage';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import { useState } from 'react';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
const mockPdf = buildLgSearchResult();
const mockPatientDetails = buildPatientDetails();

describe('LgRecordStage', () => {
    it('renders an lg record', async () => {
        renderComponent();

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });
        expect(screen.getByText('View record')).toBeInTheDocument();
        expect(screen.getByText('View in full screen')).toBeInTheDocument();

        expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        expect(screen.queryByText('No documents are available')).not.toBeInTheDocument();
        expect(
            screen.getByText('7 files | File size: 7 bytes | File format: PDF'),
        ).toBeInTheDocument();
    });

    it('renders no docs available text if there is no LG record', async () => {
        renderComponent({
            downloadStage: DOWNLOAD_STAGE.FAILED,
        });

        await waitFor(async () => {
            expect(screen.getByText('No documents are available')).toBeInTheDocument();
        });

        expect(screen.queryByText('View record')).not.toBeInTheDocument();
    });

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

    it("returns to previous view when 'Go back' link clicked during full screen", async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });

        userEvent.click(screen.getByText('View in full screen'));

        await waitFor(() => {
            expect(screen.queryByText('Lloyd George record')).not.toBeInTheDocument();
        });

        userEvent.click(screen.getByText('Go back'));

        await waitFor(() => {
            expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        });
    });
});
const TestApp = (props: Omit<Props, 'setStage'>) => {
    const [, setStage] = useState(LG_RECORD_STAGE.RECORD);
    return <LgRecordStage {...props} setStage={setStage} />;
};

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage'> = {
        patientDetails: mockPatientDetails,
        downloadStage: DOWNLOAD_STAGE.SUCCEEDED,
        lloydGeorgeUrl: mockPdf.presign_url,
        lastUpdated: mockPdf.last_updated,
        numberOfFiles: mockPdf.number_of_files,
        totalFileSizeInByte: mockPdf.total_file_size_in_byte,

        ...propsOverride,
    };
    render(<TestApp {...props} />);
};
