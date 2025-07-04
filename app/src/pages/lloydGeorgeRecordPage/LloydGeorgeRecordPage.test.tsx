import { render, screen, waitFor } from '@testing-library/react';
import { act } from 'react';
import LloydGeorgeRecordPage from './LloydGeorgeRecordPage';
import {
    buildPatientDetails,
    buildLgSearchResult,
    buildConfig,
} from '../../helpers/test/testBuilders';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import axios from 'axios';
import usePatient from '../../helpers/hooks/usePatient';
import useConfig from '../../helpers/hooks/useConfig';
import useRole from '../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import * as ReactRouter from 'react-router-dom';
import { History, createMemoryHistory } from 'history';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import SessionProvider from '../../providers/sessionProvider/SessionProvider';
import { afterEach, beforeEach, describe, expect, it, vi, Mock, Mocked } from 'vitest';

vi.mock('axios');
vi.mock('../../helpers/hooks/useConfig');
vi.mock('../../helpers/hooks/usePatient');
vi.mock('../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../helpers/hooks/useRole');

const mockAxios = axios as Mocked<typeof axios>;
const mockPatientDetails = buildPatientDetails();
const mockedUsePatient = usePatient as Mock;
const mockNavigate = vi.fn();
const mockUseConfig = useConfig as Mock;
const mockUseRole = useRole as Mock;

vi.mock('react-router-dom', async () => ({
    ...(await vi.importActual('react-router-dom')),
    Link: (props: ReactRouter.LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));
Date.now = () => new Date('2020-01-01T00:00:00.000Z').getTime();

let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('LloydGeorgeRecordPage', () => {
    global.URL.createObjectURL = vi.fn().mockReturnValue('http://localhost');
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });

        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        mockedUsePatient.mockReturnValue(mockPatientDetails);
        mockUseConfig.mockReturnValue(buildConfig());
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders patient details', async () => {
        const patientName = `${mockPatientDetails.givenName}, ${mockPatientDetails.familyName}`;
        const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));
        mockAxios.get.mockReturnValue(Promise.resolve({ data: buildLgSearchResult() }));

        await act(async () => {
            await renderPage(history);
        });

        await waitFor(async () => {
            expect(screen.getByText(patientName)).toBeInTheDocument();
        });
        expect(screen.getByText(`Date of birth: ${dob}`)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
    });

    it('renders initial lg record view', async () => {
        await act(async () => {
            await renderPage(history);
        });
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

        mockAxios.post.mockImplementation(() => Promise.reject(errorResponse));

        await act(async () => {
            await renderPage(history);
        });

        await waitFor(async () => {
            expect(
                screen.getByText(
                    'This patient does not have a Lloyd George record stored in this service.',
                ),
            ).toBeInTheDocument();
        });
    });

    it('renders initial lg record view with no docs available text if lambda return records status is uploading for more than 3 min', async () => {
        const errorResponse = {
            response: {
                status: 400,
                data: { err_code: 'LGL_400', message: '400 no docs found' },
                message: '400 no docs found',
            },
        };

        mockAxios.post.mockImplementation(() => Promise.reject(errorResponse));

        await act(async () => {
            await renderPage(history);
        });

        await waitFor(async () => {
            expect(
                screen.getByText(
                    'This patient does not have a Lloyd George record stored in this service.',
                ),
            ).toBeInTheDocument();
        });
        expect(screen.queryByTestId('record-menu-card')).not.toBeInTheDocument();
    });

    it('renders initial lg record view with docs are uploading text if response status is 423', async () => {
        const errorResponse = {
            response: {
                status: 423,
                data: { err_code: 'LGL_423', message: '423' },
                message: '423',
            },
        };

        mockAxios.post.mockImplementation(() => Promise.reject(errorResponse));

        await act(async () => {
            await renderPage(history);
        });

        await waitFor(async () => {
            expect(
                screen.getByText(
                    'You can view this record once it’s finished uploading. This may take a few minutes.',
                ),
            ).toBeInTheDocument();
        });
    });

    it('renders initial lg record view with timeout text if response is 504', async () => {
        const errorResponse = {
            response: {
                status: 504,
                message: '504 no docs found',
            },
        };

        mockAxios.post.mockImplementation(() => Promise.reject(errorResponse));
        mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);

        await act(async () => {
            await renderPage(history);
        });

        await waitFor(async () => {
            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i),
            ).toBeInTheDocument();
        });
        expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
    });

    it('displays Loading... until the pdf is fetched', async () => {
        mockAxios.get.mockReturnValue(Promise.resolve({ data: buildLgSearchResult() }));

        act(() => {
            renderPage(history);
        });

        await waitFor(async () => {
            expect(screen.getByText('Loading...')).toBeInTheDocument();
        });
    });

    it('renders initial lg record view with file info when LG record is returned by search', async () => {
        const lgResult = buildLgSearchResult();
        mockAxios.post.mockResolvedValue({ data: { jobStatus: 'Pending' } });

        mockAxios.get.mockResolvedValue({ data: lgResult });

        await renderPage(history);

        expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        expect(screen.queryByText('No documents are available')).not.toBeInTheDocument();
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            const lgResult = buildLgSearchResult();
            mockAxios.post.mockResolvedValue({ data: { jobStatus: 'Pending' } });

            mockAxios.get.mockResolvedValue({ data: lgResult });

            await renderPage(history);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    const renderPage = async (history: History) => {
        await act(async () => {
            return render(
                <SessionProvider sessionOverride={{ isLoggedIn: true }}>
                    <ReactRouter.Router navigator={history} location={history.location}>
                        <LloydGeorgeRecordPage />
                    </ReactRouter.Router>
                    ,
                </SessionProvider>,
            );
        });
    };
});
