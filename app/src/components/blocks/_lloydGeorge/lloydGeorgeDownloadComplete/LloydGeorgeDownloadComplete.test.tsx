import usePatient from '../../../../helpers/hooks/usePatient';
import { routes } from '../../../../types/generic/routes';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import { act, render, screen, waitFor } from '@testing-library/react';
import LloydGeorgeDownloadComplete from './LloydGeorgeDownloadComplete';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import LgDownloadComplete from './LloydGeorgeDownloadComplete';
import userEvent from '@testing-library/user-event';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import React from 'react';

jest.mock('../../../../helpers/hooks/usePatient');

const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;

const mockNavigate = jest.fn();

jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));

const numberOfFiles = 7;
const selectedDocuments = ['test-id-1', 'test-id-2'];
const downloadAllSelectedDocuments: Array<string> = [];
const searchResults = [
    buildSearchResult({ fileName: '1of2_test.pdf', ID: 'test-id-1' }),
    buildSearchResult({ fileName: '2of2_test.pdf', ID: 'test-id-2' }),
    buildSearchResult({ fileName: '1of1_test.pdf', ID: 'test-id-3' }),
];

describe('LloydGeorgeDownloadComplete', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });


    it('navigates to the view Lloyd George page when back to medical records is clicked', async () => {
        render(<LgDownloadComplete
            deleteAfterDownload={false}
            numberOfFiles={selectedDocuments.length}
            selectedDocuments={selectedDocuments}
            searchResults={searchResults} />);

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
            expect(mockNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
        });
    });

    it('display record removed text if deleteAfterDownload is true', async () => {
        render(
            <LgDownloadComplete
                deleteAfterDownload={true}
                numberOfFiles={selectedDocuments.length}
                selectedDocuments={selectedDocuments}
                searchResults={searchResults}
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
});

describe('LloydGeorgeDownloadComplete non BSOL journey', () => {
    it('renders the component', () => {
        render(
            <LloydGeorgeDownloadComplete
                deleteAfterDownload={false}
                numberOfFiles={selectedDocuments.length}
                selectedDocuments={selectedDocuments}
                searchResults={searchResults}
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

    // it('calls set stage AND set download stage when delete after download is true', () => {
    //     render(
    //         <LloydGeorgeDownloadComplete
    //             setStage={mockSetStage}
    //             setDownloadStage={mockSetDownloadStage}
    //             deleteAfterDownload={true}
    //             numberOfFiles={numberOfFiles}
    //         />,
    //     );

    //         userEvent.click(
    //         screen.getByRole('button', {
    //             name: 'Return to patient record',
    //         }),
    //     );

    //     expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
    //     expect(mockSetDownloadStage).toHaveBeenCalledWith(DOWNLOAD_STAGE.REFRESH);
    // });
});


describe('LloydGeorgeDownloadComplete BSOL journeys', () => {
    it('renders the download complete screen for download all journey', () => {
        render(
            <LgDownloadComplete
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

    // it('calls set stage when delete after download is false', () => {
    //     render(
    //         <LloydGeorgeDownloadComplete
    //             deleteAfterDownload={false}
    //             numberOfFiles={downloadAllSelectedDocuments.length}
    //             selectedDocuments={downloadAllSelectedDocuments}
    //             searchResults={searchResults}
    //         />,
    //     );

    //     userEvent.click(
    //         screen.getByRole('button', {
    //             name: 'Return to patient record',
    //         }),
    //     );

    //     expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
    //     expect(mockSetDownloadStage).not.toBeCalled();
    // });

    it('renders the download complete screen for download selected files journey', () => {
        render(
            <LgDownloadComplete
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
        expect(screen.getByText('1of2_test.pdf')).toBeInTheDocument();
        expect(screen.getByText('2of2_test.pdf')).toBeInTheDocument();
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

describe('Accessibility', () => {
    it.each([true, false])(
        'pass accessibility checks when deleteAfterDownload is %s',
        async (deleteAfterDownload) => {
            render(
                <LloydGeorgeDownloadComplete
                    numberOfFiles={numberOfFiles}
                    deleteAfterDownload={deleteAfterDownload}
                />,
            );

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        },
    );
});