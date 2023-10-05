import { render, screen, waitFor } from '@testing-library/react';
import { USER_ROLE } from '../../types/generic/roles';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { PatientDetails } from '../../types/generic/patientDetails';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import PatientSearchPage, { incorrectFormatMessage } from './PatientSearchPage';
import userEvent from '@testing-library/user-event';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import axios from 'axios';
import { routes } from '../../types/generic/routes';
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('PatientSearchPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('displays component with patient details', () => {
            renderPatientSearchPage();
            expect(screen.getByText('Search for patient')).toBeInTheDocument();
            expect(screen.getByRole('textbox', { name: 'Enter NHS number' })).toBeInTheDocument();
            expect(
                screen.getByText('A 10-digit number, for example, 485 777 3456'),
            ).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
        });

        it('displays a loading spinner when the patients details are being requested', async () => {
            mockedAxios.get.mockImplementation(async () => {
                await new Promise((resolve) => {
                    setTimeout(() => {
                        // To delay the mock request, and give a chance for the spinner to appear
                        resolve(null);
                    }, 500);
                });
                return Promise.resolve({ data: buildPatientDetails() });
            });

            renderPatientSearchPage();

            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000009');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(screen.getByRole('SpinnerButton')).toBeInTheDocument();
            });
        });

        it('displays an input error when user attempts to submit an invalid NHS number', async () => {
            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '21212');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            await waitFor(() => {
                expect(screen.getByText(incorrectFormatMessage)).toBeInTheDocument();
            });
        });
    });

    describe('Axios', () => {
        it('returns an input error axios response is patient not found', async () => {
            const errorResponse = {
                response: {
                    status: 400,
                    message: '400 Patient not found.',
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '0987654321');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            expect(await screen.findAllByText('Enter a valid patient NHS number.')).toHaveLength(2);
        });

        it('returns an input error when patient data not found', async () => {
            const errorResponse = {
                response: {
                    status: 404,
                    message: '404 Not found.',
                },
            };

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '0987654321');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            expect(await screen.findAllByText('Sorry, patient data not found.')).toHaveLength(2);
        });

        it('returns a service error when service is down', async () => {
            const errorResponse = {
                response: {
                    status: 500,
                    message: '500 Unknown Service Error.',
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '0987654321');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            await waitFor(() => {
                expect(
                    screen.getByText('Sorry, the service is currently unavailable.'),
                ).toBeInTheDocument();
            });
        });
    });

    describe('Navigation', () => {
        it('navigates to verify page when download patient is requested', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });

            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: buildPatientDetails() }),
            );

            renderPatientSearchPage({}, USER_ROLE.PCSE, history);
            expect(history.location.pathname).toBe('/example');
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000000');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.DOWNLOAD_VERIFY);
            });
        });

        it('navigates to verify page when upload patient is requested', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });

            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: buildPatientDetails() }),
            );
            renderPatientSearchPage({}, USER_ROLE.GP, history);
            expect(history.location.pathname).toBe('/example');
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000000');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.UPLOAD_VERIFY);
            });
        });

        it('navigates to start page when user is unauthorized to make request', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });
            const errorResponse = {
                response: {
                    status: 403,
                    message: '403 Unauthorized.',
                },
            };

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage({}, USER_ROLE.GP, history);
            expect(history.location.pathname).toBe('/example');
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000000');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.HOME);
            });
        });
    });

    describe('Validation', () => {
        it('allows NHS number with spaces to be submitted', async () => {
            const testNumber = '900 000 0000';
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });

            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: buildPatientDetails() }),
            );

            renderPatientSearchPage({}, USER_ROLE.PCSE, history);
            expect(history.location.pathname).toBe('/example');
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), testNumber);
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.DOWNLOAD_VERIFY);
            });
        });

        it('allows NHS number with dashes to be submitted', async () => {
            const testNumber = '900-000-0000';
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });

            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: buildPatientDetails() }),
            );

            renderPatientSearchPage({}, USER_ROLE.PCSE, history);
            expect(history.location.pathname).toBe('/example');
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), testNumber);
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.DOWNLOAD_VERIFY);
            });
        });

        it('does not allow missing NHS number', async () => {
            renderPatientSearchPage();
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            await waitFor(() => {
                expect(screen.getByText(incorrectFormatMessage)).toBeInTheDocument();
            });
        });

        it.each([['123456789'], ['12345678901'], ['123456789A']])(
            "does not allow the NHS number '%s''",
            async (nhsNumber) => {
                renderPatientSearchPage();
                userEvent.type(
                    screen.getByRole('textbox', { name: 'Enter NHS number' }),
                    nhsNumber,
                );
                userEvent.click(screen.getByRole('button', { name: 'Search' }));
                await waitFor(() => {
                    expect(screen.getByText(incorrectFormatMessage)).toBeInTheDocument();
                });
            },
        );
    });
});

const testRoute = '/example';
const renderPatientSearchPage = (
    patientOverride: Partial<PatientDetails> = {},
    role: USER_ROLE = USER_ROLE.PCSE,
    history = createMemoryHistory({
        initialEntries: [testRoute],
        initialIndex: 1,
    }),
) => {
    const patient: PatientDetails = {
        ...buildPatientDetails(),
        ...patientOverride,
    };
    const needsPatient = !!Object.keys(patientOverride).length;
    render(
        <ReactRouter.Router navigator={history} location={testRoute}>
            <PatientDetailsProvider patientDetails={needsPatient ? patient : undefined}>
                <PatientSearchPage role={role} />
            </PatientDetailsProvider>
        </ReactRouter.Router>,
    );
};
