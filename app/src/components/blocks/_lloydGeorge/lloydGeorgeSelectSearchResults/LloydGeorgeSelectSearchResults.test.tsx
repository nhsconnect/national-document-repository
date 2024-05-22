import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import { LinkProps } from 'react-router-dom';
import { act } from 'react-dom/test-utils';
import LloydGeorgeSelectSearchResults from './LloydGeorgeSelectSearchResults';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';
import { SEARCH_AND_DOWNLOAD_STATE } from '../../../../types/pages/documentSearchResultsPage/types';

jest.mock('../../../../helpers/hooks/usePatient');
jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

window.scrollTo = jest.fn() as jest.Mock;
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();
const mockSetSelectedDocuments = jest.fn();
const mockSetSubmissionSearchState = jest.fn();
const mockSelectedDocuments = ['test-id-1', 'test-id-2'];
const searchResults = [
    buildSearchResult({ fileName: '1of2_test.pdf', ID: 'test-id-1' }),
    buildSearchResult({ fileName: '2of2_test.pdf', ID: 'test-id-2' }),
    buildSearchResult({ fileName: '1of1_test.pdf', ID: 'test-id-3' }),
];

describe('LloydGeorgeSelectSearchResults', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page', () => {
        render(
            <LloydGeorgeSelectSearchResults
                searchResults={searchResults}
                setSubmissionSearchState={mockSetSubmissionSearchState}
                selectedDocuments={mockSelectedDocuments}
                setSelectedDocuments={mockSetSelectedDocuments}
            />,
        );

        expect(
            screen.getByRole('heading', {
                name: 'Download the Lloyd George record for this patient',
            }),
        ).toBeInTheDocument();
        expect(screen.getByTestId('available-files-table-title')).toBeInTheDocument();
        expect(screen.getByTestId('search-result-0')).toBeInTheDocument();
        expect(screen.getByTestId('search-result-1')).toBeInTheDocument();
        expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        expect(screen.getByTestId('download-selected-files-btn')).toBeInTheDocument();
        expect(screen.getByTestId('download-all-files-btn')).toBeInTheDocument();
        expect(screen.getByTestId('start-again-link')).toBeInTheDocument();
    });

    it('navigates to start page when user clicks on start again link', () => {
        render(
            <LloydGeorgeSelectSearchResults
                searchResults={searchResults}
                setSubmissionSearchState={mockSetSubmissionSearchState}
                selectedDocuments={mockSelectedDocuments}
                setSelectedDocuments={mockSetSelectedDocuments}
            />,
        );

        act(() => {
            userEvent.click(screen.getByRole('link', { name: 'Start again' }));
        });

        expect(mockNavigate).toHaveBeenCalledWith(routes.START);
    });

    it('sets submission state when download selected files button is clicked and not all files selected', () => {
        render(
            <LloydGeorgeSelectSearchResults
                searchResults={searchResults}
                setSubmissionSearchState={mockSetSubmissionSearchState}
                selectedDocuments={mockSelectedDocuments}
                setSelectedDocuments={mockSetSelectedDocuments}
            />,
        );

        act(() => {
            userEvent.click(screen.getByTestId('download-selected-files-btn'));
        });

        expect(mockSetSubmissionSearchState).toHaveBeenCalledWith(
            SEARCH_AND_DOWNLOAD_STATE.DOWNLOAD_SELECTED,
        );
    });

    it('sets submission state and empties selected docs array when download selected files button is clicked but all files selected', () => {
        render(
            <LloydGeorgeSelectSearchResults
                searchResults={searchResults}
                setSubmissionSearchState={mockSetSubmissionSearchState}
                selectedDocuments={['test-id-1', 'test-id-2', 'test-id-3']}
                setSelectedDocuments={mockSetSelectedDocuments}
            />,
        );

        act(() => {
            userEvent.click(screen.getByTestId('download-selected-files-btn'));
        });

        expect(mockSetSelectedDocuments).toHaveBeenCalledWith([]);
        expect(mockSetSubmissionSearchState).toHaveBeenCalledWith(
            SEARCH_AND_DOWNLOAD_STATE.DOWNLOAD_SELECTED,
        );
    });

    it('shows error box when download selected files button is clicked but no files selected', async () => {
        render(
            <LloydGeorgeSelectSearchResults
                searchResults={searchResults}
                setSubmissionSearchState={mockSetSubmissionSearchState}
                selectedDocuments={[]}
                setSelectedDocuments={mockSetSelectedDocuments}
            />,
        );

        act(() => {
            userEvent.click(screen.getByTestId('download-selected-files-btn'));
        });

        await waitFor(() => {
            expect(screen.getByTestId('download-selection-error-box')).toBeInTheDocument();
        });
        expect(window.scrollTo).toHaveBeenCalledWith(0, 0);
    });
});