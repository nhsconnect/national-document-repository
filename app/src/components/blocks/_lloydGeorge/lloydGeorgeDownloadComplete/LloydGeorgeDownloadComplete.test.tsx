import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import { render, screen, waitFor } from '@testing-library/react';
import LloydGeorgeDownloadComplete from './LloydGeorgeDownloadComplete';
import userEvent from '@testing-library/user-event';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import LgDownloadComplete from './LloydGeorgeDownloadComplete';
import React from 'react';

jest.mock('../../../../helpers/hooks/usePatient');

const mockSetStage = jest.fn();
const mockSetDownloadStage = jest.fn();
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNumberOfFiles = 7;

describe('LloydGeorgeDownloadComplete', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('LloydGeorgeDownloadComplete non BSOL journey', () => {
        it('renders the component', () => {
            render(
                <LloydGeorgeDownloadComplete
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                    deleteAfterDownload={true}
                    numberOfFiles={mockNumberOfFiles}
                />,
            );

            expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
            expect(
                screen.getByText('You have successfully downloaded the Lloyd George record of:'),
            ).toBeInTheDocument();
            expect(
                screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', {
                    name: 'Return to patient record',
                }),
            ).toBeInTheDocument();
        });

        it('display record removed text if deleteAfterDownload is true', async () => {
            render(
                <LloydGeorgeDownloadComplete
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                    deleteAfterDownload={true}
                    numberOfFiles={mockNumberOfFiles}
                />,
            );

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

        it('calls set stage AND set download stage when delete after download is true', () => {
            render(
                <LloydGeorgeDownloadComplete
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                    deleteAfterDownload={true}
                    numberOfFiles={mockNumberOfFiles}
                />,
            );

            userEvent.click(
                screen.getByRole('button', {
                    name: 'Return to patient record',
                }),
            );

            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
            expect(mockSetDownloadStage).toHaveBeenCalledWith(DOWNLOAD_STAGE.REFRESH);
        });
    });

    describe('LloydGeorgeDownloadComplete BSOL journeys', () => {
        xit('renders the component', () => {
            // render(
            //     <LgDownloadComplete
            //         setStage={mockSetStage}
            //         setDownloadStage={mockSetDownloadStageStage}
            //         deleteAfterDownload={false}
            //         numberOfFiles={mockNumberOfFiles}
            //         selectedDocuments={selectedDocuments}
            //         searchResults={searchResults}
            //     />
            // );

            expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
            expect(
                screen.getByText('You have successfully downloaded the Lloyd George record of:'),
            ).toBeInTheDocument();
            expect(
                screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', {
                    name: 'Return to patient record',
                }),
            ).toBeInTheDocument();
        });
    });
});
