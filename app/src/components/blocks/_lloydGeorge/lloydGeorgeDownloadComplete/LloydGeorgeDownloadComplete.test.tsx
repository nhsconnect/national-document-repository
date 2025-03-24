import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import { render, screen } from '@testing-library/react';
import LloydGeorgeDownloadComplete from './LloydGeorgeDownloadComplete';
import LgDownloadComplete from './LloydGeorgeDownloadComplete';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import React from 'react';

jest.mock('../../../../helpers/hooks/usePatient');

const mockedUseNavigate = jest.fn();
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockSetDownloadStage = jest.fn();

const numberOfFiles = 7;
const selectedDocuments = ['test-id-1', 'test-id-2'];
const downloadAllSelectedDocuments: Array<string> = [];
const searchResults = [
    buildSearchResult({ fileName: '1of2_test.pdf', ID: 'test-id-1' }),
    buildSearchResult({ fileName: '2of2_test.pdf', ID: 'test-id-2' }),
    buildSearchResult({ fileName: '1of1_test.pdf', ID: 'test-id-3' }),
];

jest.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('LloydGeorgeDownloadComplete', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('LloydGeorgeDownloadComplete  journeys', () => {
        it('renders the download complete screen for download all journey', () => {
            render(
                <LgDownloadComplete
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

        it('renders the download complete screen for download selected files journey', () => {
            render(
                <LgDownloadComplete
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
        it('pass accessibility checks', () => {
            render(<LloydGeorgeDownloadComplete numberOfFiles={numberOfFiles} />);
            const results = runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });
});
