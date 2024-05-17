import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import LloydGeorgeSelectDownloadStage from './LloydGeorgeSelectDownloadStage';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import { LinkProps } from 'react-router-dom';
import axios from 'axios';
import { act } from 'react-dom/test-utils';
import LloydGeorgeRecordPage from '../../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { routes } from '../../../../types/generic/routes';
import { errorToParams } from '../../../../helpers/utils/errorToParams';

jest.mock('../../../../helpers/hooks/usePatient');
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('axios');
jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));
jest.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});

const mockAxios = axios as jest.Mocked<typeof axios>;
const mockSetStage = jest.fn();
const mockSetDownloadStage = jest.fn();
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();
const mockSetSearchResults = jest.fn();
const mockSetSubmissionSearchState = jest.fn();

const searchResults = [
    buildSearchResult({ fileName: '1of2_test.pdf', ID: 'test-id-1' }),
    buildSearchResult({ fileName: '2of2_test.pdf', ID: 'test-id-2' }),
    buildSearchResult({ fileName: '1of1_test.pdf', ID: 'test-id-3' }),
];

describe('LloydGeorgeSelectDownloadStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header, patient details and loading text on page load', () => {
        act(() => {
            render(
                <LloydGeorgeSelectDownloadStage
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                />,
            );
        });

        expect(
            screen.getByRole('heading', {
                name: 'Download the Lloyd George record for this patient',
            }),
        ).toBeInTheDocument();

        expect(screen.getByText('NHS number')).toBeInTheDocument();
        expect(screen.getByText(`${mockPatient.nhsNumber}`)).toBeInTheDocument();
        expect(screen.getByText('Surname')).toBeInTheDocument();
        expect(screen.getByText(`${mockPatient.familyName}`)).toBeInTheDocument();
        expect(screen.getByText('First name')).toBeInTheDocument();
        expect(screen.getByText(`${mockPatient.givenName}`)).toBeInTheDocument();
        expect(screen.getByText('Date of birth')).toBeInTheDocument();
        expect(
            screen.getByText(getFormattedDate(new Date(mockPatient.birthDate))),
        ).toBeInTheDocument();
        expect(screen.getByText('Postcode')).toBeInTheDocument();
        expect(screen.getByText(`${mockPatient.postalCode}`)).toBeInTheDocument();

        expect(screen.getByText('Loading...')).toBeInTheDocument();
        expect(screen.queryByTestId('available-files-table-title')).not.toBeInTheDocument();
    });

    it('calls set search results and set submission search state when axios get request is successful', async () => {
        mockAxios.get.mockReturnValue(Promise.resolve({ data: searchResults }));

        act(() => {
            render(
                <LloydGeorgeSelectDownloadStage
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                />,
            );
        });

        await waitFor(async () => {
            expect(screen.getByTestId('available-files-table-title')).toBeInTheDocument();
        });
        expect(screen.getByTestId('search-result-0')).toBeInTheDocument();
        expect(screen.getByTestId('download-selected-files-btn')).toBeInTheDocument();
        expect(screen.getByTestId('download-all-files-btn')).toBeInTheDocument();
        expect(screen.getByTestId('start-again-link')).toBeInTheDocument();
    });

    it('navigates to session expired page when get request returns 403', async () => {
        const errorResponse = {
            response: {
                status: 403,
                data: { message: 'Unauthorised' },
            },
        };
        mockAxios.get.mockImplementation(() => Promise.reject(errorResponse));

        act(() => {
            render(
                <LloydGeorgeSelectDownloadStage
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                />,
            );
        });

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
        });
    });

    it('navigates to server error page when get request returns 5XX', async () => {
        const errorResponse = {
            response: {
                status: 500,
                data: { message: 'Server error', err_code: 'SP_1001' },
            },
        };
        mockAxios.get.mockImplementation(() => Promise.reject(errorResponse));

        act(() => {
            render(
                <LloydGeorgeSelectDownloadStage
                    setStage={mockSetStage}
                    setDownloadStage={mockSetDownloadStage}
                />,
            );
        });

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith(
                routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
            );
        });
    });
});
