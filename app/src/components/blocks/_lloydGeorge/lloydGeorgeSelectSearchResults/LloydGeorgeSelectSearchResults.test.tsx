import { act, render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import { LinkProps } from 'react-router-dom';
import LloydGeorgeSelectSearchResults, { Props } from './LloydGeorgeSelectSearchResults';
import userEvent from '@testing-library/user-event';
import { SEARCH_AND_DOWNLOAD_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

window.scrollTo = vi.fn() as Mock;
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as Mock;
const mockNavigate = vi.fn();
const mockSetSelectedDocuments = vi.fn();
const mockSetSubmissionSearchState = vi.fn();
const mockSelectedDocuments = ['test-id-1', 'test-id-2'];
const searchResults = [
    buildSearchResult({ fileName: '1of2_test.pdf', id: 'test-id-1' }),
    buildSearchResult({ fileName: '2of2_test.pdf', id: 'test-id-2' }),
    buildSearchResult({ fileName: '1of1_test.pdf', id: 'test-id-3' }),
];
const searchResultOneFileOnly = [searchResults[0]];
const mockAllSelectedDocuments = [searchResults[2].id, searchResults[0].id, searchResults[1].id];

describe('LloydGeorgeSelectSearchResults', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        vi.clearAllMocks();
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
        });

        it('renders the correct table headers', () => {
            renderComponent({ selectedDocuments: mockSelectedDocuments });

            const headers = screen.getAllByRole('columnheader');
            const expectedHeaders = ['Selected', 'Upload date', 'File size'];

            expectedHeaders.forEach((headerText, index) => {
                expect(headers[index]).toHaveTextContent(headerText);
            });

            const filesTable = screen.getByTestId('available-files-table-title');
            expect(filesTable).toHaveTextContent(/bytes|KB|MB|GB/);
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
            const expectedSelectedDocument = [...mockSelectedDocuments, searchResults[2].id];

            const checkbox = screen.getByRole('checkbox', {
                name: `Select Filename ${searchResults[2].fileName}`,
            });
            expect(checkbox).not.toBeChecked();

            act(() => {
                userEvent.click(checkbox);
            });
            expect(mockSetSelectedDocuments).toBeCalledWith(expectedSelectedDocument);
        });

        it('remove documentId from selectedDocument when a checkbox is unchecked', async () => {
            renderComponent({ selectedDocuments: mockSelectedDocuments });
            const expectedSelectedDocument = mockSelectedDocuments.filter(
                (id) => id !== searchResults[0].id,
            );

            const checkbox = screen.getByRole('checkbox', {
                name: `Select Filename ${searchResults[0].fileName}`,
            });
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
            expect(screen.getByTestId('download-file-btn')).toBeInTheDocument();
            expect(screen.queryByTestId('toggle-selection-btn')).not.toBeInTheDocument();
        });

        describe('Toggle select all button', () => {
            it('checks all checkboxes are checked when select all files button is clicked, no files previously checked', async () => {
                let selectedDocuments: Array<string> = [];
                mockSetSelectedDocuments.mockImplementation(
                    (documents) => (selectedDocuments = documents),
                );

                const { rerender } = renderComponent({ selectedDocuments: [] });
                const toggleSelectAllBtn = screen.getByTestId('toggle-selection-btn');
                const checkboxes = screen.getAllByRole('checkbox');

                act(() => {
                    userEvent.click(toggleSelectAllBtn);
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

                expect(toggleSelectAllBtn).toHaveTextContent('Deselect all files');
                expect(toggleSelectAllBtn).toHaveTextContent('All files are selected');
            });

            it('check all checkboxes unchecked, when select all files button clicked, all files previously checked', () => {
                let selectedDocuments = mockAllSelectedDocuments;
                mockSetSelectedDocuments.mockImplementation(
                    (documents) => (selectedDocuments = documents),
                );

                const { rerender } = renderComponent({
                    selectedDocuments: mockAllSelectedDocuments,
                });
                const toggleSelectAllBtn = screen.getByTestId('toggle-selection-btn');
                const checkboxes = screen.getAllByRole('checkbox');

                checkboxes.forEach((checkbox) => {
                    expect(checkbox).toBeChecked();
                });

                expect(toggleSelectAllBtn).toHaveTextContent('Deselect all files');
                expect(toggleSelectAllBtn).toHaveTextContent('All files are selected');

                act(() => {
                    userEvent.click(toggleSelectAllBtn);
                });

                expect(mockSetSelectedDocuments).toBeCalledWith([]);

                const props: Props = {
                    searchResults: searchResults,
                    setSubmissionSearchState: mockSetSubmissionSearchState,
                    selectedDocuments: selectedDocuments,
                    setSelectedDocuments: mockSetSelectedDocuments,
                };

                rerender(<LloydGeorgeSelectSearchResults {...props} />);

                checkboxes.forEach((checkbox) => {
                    expect(checkbox).not.toBeChecked();
                });
                expect(toggleSelectAllBtn).toHaveTextContent('Select all files');
                expect(toggleSelectAllBtn).toHaveTextContent('All files are deselected');
            });

            it('check all checkboxes unchecked, when select all files button clicked twice, no files previously checked', () => {
                const props: Props = {
                    searchResults: searchResults,
                    setSubmissionSearchState: mockSetSubmissionSearchState,
                    selectedDocuments: [],
                    setSelectedDocuments: mockSetSelectedDocuments,
                };
                mockSetSelectedDocuments.mockImplementation(
                    (documents) => (props.selectedDocuments = documents),
                );

                const { rerender } = renderComponent(props);
                const toggleSelectAllBtn = screen.getByTestId('toggle-selection-btn');
                const checkboxes = screen.getAllByRole('checkbox');

                act(() => {
                    userEvent.click(toggleSelectAllBtn);
                });

                rerender(<LloydGeorgeSelectSearchResults {...props} />);

                act(() => {
                    userEvent.click(toggleSelectAllBtn);
                });

                expect(mockSetSelectedDocuments).toBeCalledWith([]);

                rerender(<LloydGeorgeSelectSearchResults {...props} />);

                checkboxes.forEach((checkbox) => {
                    expect(checkbox).not.toBeChecked();
                });
                expect(toggleSelectAllBtn).toHaveTextContent('Select all files');
                expect(toggleSelectAllBtn).toHaveTextContent('All files are deselected');
            });
        });
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            renderComponent();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it.skip('pass accessibility checks when error box shows up', async () => {
            renderComponent({ selectedDocuments: [] });

            act(() => {
                userEvent.click(screen.getByTestId('download-selected-files-btn'));
            });

            await waitFor(expect(screen.getByRole('alert')).toBeInTheDocument);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('check all checkboxes have aria-checked attribute', () => {
            renderComponent();
            const allCheckBoxes = screen.getAllByRole('checkbox');

            allCheckBoxes.forEach((checkbox) => {
                expect(checkbox).toHaveAttribute('aria-checked');
            });
        });
        it('checkbox has aria-checked attribute reflecting the checkbox status', () => {
            const props: Props = {
                searchResults: searchResults,
                setSubmissionSearchState: mockSetSubmissionSearchState,
                selectedDocuments: [],
                setSelectedDocuments: mockSetSelectedDocuments,
            };
            mockSetSelectedDocuments.mockImplementation(
                (documents) => (props.selectedDocuments = documents),
            );

            const { rerender } = renderComponent(props);
            const firstCheckBox = screen.getByTestId('checkbox-0');

            expect(firstCheckBox).toHaveAttribute('aria-checked', 'false');

            act(() => {
                userEvent.click(firstCheckBox);
            });

            rerender(<LloydGeorgeSelectSearchResults {...props} />);

            expect(firstCheckBox).toHaveAttribute('aria-checked', 'true');

            act(() => {
                userEvent.click(firstCheckBox);
            });

            rerender(<LloydGeorgeSelectSearchResults {...props} />);

            expect(firstCheckBox).toHaveAttribute('aria-checked', 'false');
        });

        it('toggle select all button has status announcements associated with it', () => {
            renderComponent();
            const toggleSelectAllBtn = screen.getByTestId('toggle-selection-btn');
            const announcement = screen.getByTestId('toggle-selection-btn-announcement');
            expect(toggleSelectAllBtn).toContainElement(announcement);
        });
    });

    describe('Navigation', () => {
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
