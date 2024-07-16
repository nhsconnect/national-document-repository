import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import { LinkProps } from 'react-router-dom';
import { act } from 'react-dom/test-utils';
import LloydGeorgeSelectSearchResults, { Props } from './LloydGeorgeSelectSearchResults';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';
import { SEARCH_AND_DOWNLOAD_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';

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
const searchResultOneFileOnly = [searchResults[0]];
const mockAllSelectedDocuments = [searchResults[2].ID, searchResults[0].ID, searchResults[1].ID];

describe('LloydGeorgeSelectSearchResults', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the page', () => {
            renderComponent();

            expect(
                screen.getByRole('heading', {
                    name: 'Download the Lloyd George record for this patient',
                }),
            ).toBeInTheDocument();
            expect(screen.getByTestId('available-files-table-title')).toBeInTheDocument();
            expect(screen.getByTestId('search-result-0')).toBeInTheDocument();
            expect(screen.getByTestId('search-result-1')).toBeInTheDocument();
            expect(screen.getAllByRole('checkbox')).toHaveLength(searchResults.length);
            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
            expect(screen.getByTestId('download-selected-files-btn')).toBeInTheDocument();
            expect(screen.getByTestId('toggle-selection-btn')).toBeInTheDocument();
            expect(screen.getByTestId('start-again-link')).toBeInTheDocument();
        });

        it('shows error box when download selected files button is clicked but no files selected', async () => {
            renderComponent({ selectedDocuments: [] });

            act(() => {
                userEvent.click(screen.getByTestId('download-selected-files-btn'));
            });

            await waitFor(() => {
                expect(screen.getByTestId('download-selection-error-box')).toBeInTheDocument();
            });
            expect(window.scrollTo).toHaveBeenCalledWith(0, 0);
        });

        it('add documentId to selectedDocument when checkbox is checked', async () => {
            renderComponent({ selectedDocuments: mockSelectedDocuments });
            const expectedSelectedDocument = [...mockSelectedDocuments, searchResults[2].ID];

            const checkbox = screen.getByRole('checkbox', { name: searchResults[2].fileName });
            expect(checkbox).not.toBeChecked();

            act(() => {
                userEvent.click(checkbox);
            });
            expect(mockSetSelectedDocuments).toBeCalledWith(expectedSelectedDocument);
        });

        it('remove documentId from selectedDocument when a checkbox is unchecked', async () => {
            renderComponent({ selectedDocuments: mockSelectedDocuments });
            const expectedSelectedDocument = mockSelectedDocuments.filter(
                (id) => id !== searchResults[0].ID,
            );

            const checkbox = screen.getByRole('checkbox', { name: searchResults[0].fileName });
            expect(checkbox).toBeChecked();

            act(() => {
                userEvent.click(checkbox);
            });
            expect(mockSetSelectedDocuments).toBeCalledWith(expectedSelectedDocument);
        });

        it('does not render checkbox and `download selected file` button when there is only one file in search result', async () => {
            renderComponent({ searchResults: searchResultOneFileOnly, selectedDocuments: [] });

            expect(screen.getByTestId('search-result-0')).toBeInTheDocument();
            expect(screen.queryByRole('checkbox')).not.toBeInTheDocument();
            expect(screen.queryByTestId('download-selected-files-btn')).not.toBeInTheDocument();
            expect(screen.getByTestId('toggle-selection-btn')).toBeInTheDocument();
        });
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            renderComponent();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when error box shows up', async () => {
            renderComponent({ selectedDocuments: [] });

            act(() => {
                userEvent.click(screen.getByTestId('download-selected-files-btn'));
            });

            await waitFor(expect(screen.getByRole('alert')).toBeInTheDocument);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates to start page when user clicks on start again link', () => {
            renderComponent();

            act(() => {
                userEvent.click(screen.getByRole('link', { name: 'Start again' }));
            });

            expect(mockNavigate).toHaveBeenCalledWith(routes.START);
        });

        it('sets submission state when download selected files button is clicked and not all files selected', () => {
            renderComponent();

            act(() => {
                userEvent.click(screen.getByTestId('download-selected-files-btn'));
            });

            expect(mockSetSubmissionSearchState).toHaveBeenCalledWith(
                SEARCH_AND_DOWNLOAD_STATE.DOWNLOAD_SELECTED,
            );
        });

        it('sets submission state and empties selected docs array when download selected files button is clicked but all files selected', () => {
            renderComponent({ selectedDocuments: ['test-id-1', 'test-id-2', 'test-id-3'] });

            act(() => {
                userEvent.click(screen.getByTestId('download-selected-files-btn'));
            });

            expect(mockSetSelectedDocuments).toHaveBeenCalledWith([]);
            expect(mockSetSubmissionSearchState).toHaveBeenCalledWith(
                SEARCH_AND_DOWNLOAD_STATE.DOWNLOAD_SELECTED,
            );
        });
    });

    describe('Toggle select all button', () => {
        it('checks all checkboxes are checked when select all files button is clicked, no files previously checked', async () => {
            let selectedDocuments: Array<string> = [];
            mockSetSelectedDocuments.mockImplementation(
                (documents) => (selectedDocuments = documents),
            );

            const { rerender } = renderComponent({ selectedDocuments: [] });
            const selectAllBtn = screen.getByTestId('toggle-selection-btn');
            const checkboxes = screen.getAllByRole('checkbox');

            act(() => {
                userEvent.click(selectAllBtn);
            });

            expect(mockSetSelectedDocuments).toBeCalledWith(mockAllSelectedDocuments);

            const props: Props = {
                searchResults: searchResults,
                setSubmissionSearchState: mockSetSubmissionSearchState,
                selectedDocuments: selectedDocuments,
                setSelectedDocuments: mockSetSelectedDocuments,
            };

            rerender(<LloydGeorgeSelectSearchResults {...props} />);

            checkboxes.forEach((checkbox) => {
                expect(checkbox).toBeChecked();
            });
        });
    });
});

const renderComponent = (propsOverride: Partial<Props> = {}) => {
    const props: Props = {
        searchResults: searchResults,
        setSubmissionSearchState: mockSetSubmissionSearchState,
        selectedDocuments: mockSelectedDocuments,
        setSelectedDocuments: mockSetSelectedDocuments,
        ...propsOverride,
    };
    return render(<LloydGeorgeSelectSearchResults {...props} />);
};
