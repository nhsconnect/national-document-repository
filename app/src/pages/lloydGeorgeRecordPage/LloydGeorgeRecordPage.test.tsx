import { render, screen, waitFor } from '@testing-library/react';
import LloydGeorgeRecordPage from './LloydGeorgeRecordPage';
import {
    buildPatientDetails,
    buildLgSearchResult,
    buildSearchResult,
    buildConfig,
} from '../../helpers/test/testBuilders';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import axios from 'axios';
import formatFileSize from '../../helpers/utils/formatFileSize';
import usePatient from '../../helpers/hooks/usePatient';
import { act } from 'react-dom/test-utils';
import { routes } from '../../types/generic/routes';
import useConfig from '../../helpers/hooks/useConfig';
import { defaultFeatureFlags } from '../../types/generic/featureFlags';

jest.mock('../../helpers/hooks/useConfig');
jest.mock('axios');
jest.mock('../../helpers/hooks/usePatient');
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../helpers/hooks/useRole');
jest.mock('../../helpers/hooks/useIsBSOL');
const mockAxios = axios as jest.Mocked<typeof axios>;
const mockPatientDetails = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();
const mockUseConfig = useConfig as jest.Mock;

jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));
jest.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});

describe('LloydGeorgeRecordPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatientDetails);
        mockUseConfig.mockReturnValue(buildConfig());
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders patient details', async () => {
        const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
        const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));
        mockAxios.get.mockReturnValue(Promise.resolve({ data: buildLgSearchResult() }));

        render(<LloydGeorgeRecordPage />);

        await waitFor(async () => {
            expect(screen.getByText(patientName)).toBeInTheDocument();
        });
        expect(screen.getByText(`Date of birth: ${dob}`)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
    });

    it('renders initial lg record view', async () => {
        render(<LloydGeorgeRecordPage />);
        await waitFor(async () => {
            expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        });
    });

    it('renders initial lg record view with no docs available text if there is no LG record', async () => {
        const errorResponse = {
            response: {
                status: 404,
                message: '404 no docs found',
            },
        };

        mockAxios.get.mockImplementation(() => Promise.reject(errorResponse));

        render(<LloydGeorgeRecordPage />);

        await waitFor(async () => {
            expect(screen.getByText('No documents are available.')).toBeInTheDocument();
        });

        expect(screen.queryByText('View record')).not.toBeInTheDocument();
    });

    it('displays Loading... until the pdf is fetched', async () => {
        mockAxios.get.mockReturnValue(Promise.resolve({ data: buildLgSearchResult() }));

        render(<LloydGeorgeRecordPage />);

        await waitFor(async () => {
            expect(screen.getByText('Loading...')).toBeInTheDocument();
        });
    });

    it('renders initial lg record view with file info when LG record is returned by search', async () => {
        const lgResult = buildLgSearchResult();
        mockAxios.get.mockReturnValue(Promise.resolve({ data: lgResult }));

        render(<LloydGeorgeRecordPage />);

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });
        expect(screen.getByText('View record')).toBeInTheDocument();
        expect(screen.getByText('View in full screen')).toBeInTheDocument();

        expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        expect(screen.queryByText('No documents are available')).not.toBeInTheDocument();

        expect(screen.getByText(`${lgResult.number_of_files} files`)).toBeInTheDocument();
        expect(
            screen.getByText(`File size: ${formatFileSize(lgResult.total_file_size_in_byte)}`),
        ).toBeInTheDocument();
        expect(screen.getByText('File format: PDF')).toBeInTheDocument();
    });
    it('navigates to Error page when call to lg record view return 500', async () => {
        mockAxios.get.mockResolvedValue({ data: [buildSearchResult()] });
        const errorResponse = {
            response: {
                status: 500,
                data: { message: 'An error occurred', err_code: 'SP_1001' },
            },
        };
        mockAxios.get.mockImplementation(() => Promise.reject(errorResponse));

        act(() => {
            render(<LloydGeorgeRecordPage />);
        });

        await waitFor(() => {
            expect(screen.queryByRole('link', { name: 'Start Again' })).not.toBeInTheDocument();
        });

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith(
                routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
            );
        });
    });
});
