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
const numberOfFiles = 7;
const selectedDocuments = ['selected-doc-id-1', 'selected-doc-id-2'];
const downloadAllSelectedDocuments: Array<string> = [];
const searchResults = [
    {
        fileName: '1of2_test.pdf',
        created: '2024-01-01T14:52:00.827602Z',
        virusScannerResult: 'Clean',
        ID: 'test-id-1',
    },
    {
        fileName: '2of2_test.pdf',
        created: '2024-01-01T14:52:00.827602Z',
        virusScannerResult: 'Clean',
        ID: 'test-id-2',
    },
];

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
                    numberOfFiles={numberOfFiles}
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
            expect(screen.getByText('Your responsibilities with this record')).toBeInTheDocument();
            expect(
                screen.getByText('Follow the Record Management Code of Practice'),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', {
                    name: 'Return to patient record',
                }),
            ).toBeInTheDocument();
            expect(screen.queryByText('Hide files')).not.toBeInTheDocument();
        });

        it('calls set stage AND set download stage when delete after download is true', () => {
            render(
                <LloydGeorgeDownloadComplete
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                    deleteAfterDownload={true}
                    numberOfFiles={numberOfFiles}
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
        it('renders the download complete screen for download all journey', () => {
            render(
                <LgDownloadComplete
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                    deleteAfterDownload={false}
                    numberOfFiles={downloadAllSelectedDocuments.length}
                    selectedDocuments={downloadAllSelectedDocuments}
                    searchResults={searchResults}
                />,
            );

            expect(
                screen.getByRole('heading', { name: 'You have downloaded the record of:' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
            ).toBeInTheDocument();
            expect(screen.getByText('Your responsibilities with this record')).toBeInTheDocument();
            expect(
                screen.getByText('Follow the Record Management Code of Practice'),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', {
                    name: 'Return to patient record',
                }),
            ).toBeInTheDocument();
            expect(
                screen.queryByText('This record has been removed from our storage.'),
            ).not.toBeInTheDocument();
        });

        it('calls set stage when delete after download is false', () => {
            render(
                <LloydGeorgeDownloadComplete
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                    deleteAfterDownload={false}
                    numberOfFiles={downloadAllSelectedDocuments.length}
                    selectedDocuments={downloadAllSelectedDocuments}
                    searchResults={searchResults}
                />,
            );

            userEvent.click(
                screen.getByRole('button', {
                    name: 'Return to patient record',
                }),
            );

            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
            expect(mockSetDownloadStage).not.toBeCalled();
        });

        it('renders the download complete screen for download selected files journey', () => {
            render(
                <LgDownloadComplete
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                    deleteAfterDownload={false}
                    numberOfFiles={selectedDocuments.length}
                    selectedDocuments={selectedDocuments}
                    searchResults={searchResults}
                />,
            );

            expect(
                screen.getByRole('heading', {
                    name: 'You have downloaded files from the record of:',
                }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
            ).toBeInTheDocument();
            expect(
                screen.getByText(
                    `You have successfully downloaded ${selectedDocuments.length} file(s)`,
                ),
            ).toBeInTheDocument();
            expect(screen.getByText('Hide files')).toBeInTheDocument();
            expect(screen.getByText('Your responsibilities with this record')).toBeInTheDocument();
            expect(
                screen.getByText('Follow the Record Management Code of Practice'),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', {
                    name: 'Return to patient record',
                }),
            ).toBeInTheDocument();
            expect(
                screen.queryByText('This record has been removed from our storage.'),
            ).not.toBeInTheDocument();
        });
    });
});
