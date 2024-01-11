import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import LgDownloadComplete from './LloydGeorgeDownloadComplete';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { act } from 'react-dom/test-utils';

jest.mock('../../../helpers/hooks/usePatient');

const mockSetStage = jest.fn();
const mockDownloadStage = jest.fn();
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;

describe('LloydGeorgeDownloadComplete', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the component', () => {
        render(
            <LgDownloadComplete
                setStage={mockSetStage}
                setDownloadStage={mockDownloadStage}
                deleteAfterDownload={false}
            />,
        );

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
        render(
            <LgDownloadComplete
                setStage={mockSetStage}
                setDownloadStage={mockDownloadStage}
                deleteAfterDownload={false}
            />,
        );

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
