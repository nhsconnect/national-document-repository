import { render, screen } from '@testing-library/react';
import React from 'react';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import { LinkProps } from 'react-router-dom';
import { act } from 'react-dom/test-utils';
import LloydGeorgeSelectSearchResults from './LloydGeorgeSelectSearchResults';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';

jest.mock('../../../../helpers/hooks/usePatient');
jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();
const mockSetSelectedDocuments = jest.fn();
const selectedDocuments = ['test-id-1', 'test-id-2'];
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
        act(() => {
            render(
                <LloydGeorgeSelectSearchResults
                    searchResults={searchResults}
                    setSubmissionSearchState={jest.fn}
                    selectedDocuments={selectedDocuments}
                    setSelectedDocuments={mockSetSelectedDocuments}
                />,
            );
        });

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
        act(() => {
            render(
                <LloydGeorgeSelectSearchResults
                    searchResults={searchResults}
                    setSubmissionSearchState={jest.fn}
                    selectedDocuments={selectedDocuments}
                    setSelectedDocuments={mockSetSelectedDocuments}
                />,
            );
        });

        userEvent.click(screen.getByRole('link', { name: 'Start again' }));

        expect(mockNavigate).toHaveBeenCalledWith(routes.START);
    });
});
