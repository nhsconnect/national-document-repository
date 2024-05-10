import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { act } from 'react-dom/test-utils';

jest.mock('../../../../helpers/hooks/usePatient');

const mockSetStage = jest.fn();
const mockSetDownloadStage = jest.fn();
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;

xdescribe('LloydGeorgeDownloadComplete', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    xit('renders the component', () => {
        // render(
        //     <LgDownloadComplete
        //         setStage={mockSetStage}
        //         setDownloadStage={mockSetDownloadStage}
        //         deleteAfterDownload={false}
        //     />,
        // );

        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
        expect(
            screen.getByText('You have successfully downloaded the Lloyd George record of:'),
        ).toBeInTheDocument();
        expect(
            screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: "Return to patient's available medical records" }),
        ).toBeInTheDocument();
    });

    xit('updates the download stage view when return to medical records is clicked', async () => {
        // render(
        //     <LgDownloadComplete
        //         setStage={mockSetStage}
        //         setDownloadStage={mockSetDownloadStage}
        //         deleteAfterDownload={false}
        //     />,
        // );

        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
        expect(
            screen.getByText('You have successfully downloaded the Lloyd George record of:'),
        ).toBeInTheDocument();
        expect(
            screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
        ).toBeInTheDocument();

        const returnToRecordButton = screen.getByRole('button', {
            name: "Return to patient's available medical records",
        });
        expect(returnToRecordButton).toBeInTheDocument();
        expect(
            screen.queryByText('This record has been removed from our storage.'),
        ).not.toBeInTheDocument();

        act(() => {
            userEvent.click(returnToRecordButton);
        });

        await waitFor(async () => {
            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
        });
    });

    xit('display record removed text if deleteAfterDownload is true', async () => {
        // render(
        //     <LgDownloadComplete
        //         setStage={mockSetStage}
        //         setDownloadStage={mockSetDownloadStage}
        //         deleteAfterDownload={true}
        //     />,
        // );

        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
        expect(
            screen.getByText('You have successfully downloaded the Lloyd George record of:'),
        ).toBeInTheDocument();
        expect(
            screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
        ).toBeInTheDocument();

        expect(
            screen.getByText('This record has been removed from our storage.'),
        ).toBeInTheDocument();
    });
});
