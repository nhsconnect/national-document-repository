import { render, screen, waitFor } from '@testing-library/react';
import RemoveRecordStage from './RemoveRecordStage';
import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import axios from 'axios';
import { act } from 'react-dom/test-utils';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockUseNavigate,
}));
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../../../helpers/hooks/usePatient');
const mockUsePatient = usePatient as jest.Mock;
const mockPatientDetails = buildPatientDetails();
const mockSetStage = jest.fn();

const testFileName1 = 'John_1';
const testFileName2 = 'John_2';
const searchResults = [
    buildSearchResult({ fileName: testFileName1 }),
    buildSearchResult({ fileName: testFileName2 }),
];
describe('RemoveRecordStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockUsePatient.mockReturnValue(mockPatientDetails);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Render', () => {
        it('renders the component', () => {
            const recordType = 'Test Record';

            act(() => {
                render(<RemoveRecordStage setStage={mockSetStage} recordType={recordType} />);
            });
            expect(
                screen.getByRole('heading', { name: 'Remove this ' + recordType }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(
                    /Only permanently remove this patient record if you have a valid reason to/i,
                ),
            ).toBeInTheDocument();
            expect(screen.getByRole('link', { name: 'Go back' })).toBeInTheDocument();
        });

        it('show progress bar when file search pending', () => {
            const recordType = 'Test Record';
            mockedAxios.get.mockImplementation(() => Promise.resolve({ data: searchResults }));
            act(() => {
                render(<RemoveRecordStage setStage={mockSetStage} recordType={recordType} />);
            });
            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
        });

        it('show service error when file search failed', async () => {
            const recordType = 'Test Record';
            const errorResponse = {
                response: {
                    status: 400,
                    data: { message: 'Error', err_code: 'SP_1001' },
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            act(() => {
                render(<RemoveRecordStage setStage={mockSetStage} recordType={recordType} />);
            });
            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
            await waitFor(() => {
                expect(
                    screen.getByText(/Sorry, the service is currently unavailable/i),
                ).toBeInTheDocument();
            });

            expect(screen.getByRole('button', { name: 'Start again' })).toBeInTheDocument();
            expect(
                screen.queryByRole('button', { name: 'Remove all files' }),
            ).not.toBeInTheDocument();
        });

        it('show results when when file search succeeded', async () => {
            const recordType = 'Test Record';

            mockedAxios.get.mockImplementation(() => Promise.resolve({ data: searchResults }));

            act(() => {
                render(<RemoveRecordStage setStage={mockSetStage} recordType={recordType} />);
            });
            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
            await waitFor(() => {
                expect(
                    screen.getByRole('button', { name: 'Remove all files' }),
                ).toBeInTheDocument();
            });

            expect(screen.getByRole('button', { name: 'Start again' })).toBeInTheDocument();
            expect(screen.getByText(searchResults[0].fileName)).toBeInTheDocument();
            expect(screen.getByText(searchResults[1].fileName)).toBeInTheDocument();
        });
    });

    describe('Navigate', () => {
        it('navigates to server error page when search 500', () => {});

        it('navigates to session expired page when search 403', () => {});
    });
});
