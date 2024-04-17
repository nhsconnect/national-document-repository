import { render, screen, waitFor } from '@testing-library/react';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { PatientDetails } from '../../types/generic/patientDetails';
import PatientSearchPage, { incorrectFormatMessage } from './PatientSearchPage';
import userEvent from '@testing-library/user-event';
import { buildPatientDetails, buildSearchResult } from '../../helpers/test/testBuilders';
import axios from 'axios';
import { routes } from '../../types/generic/routes';
import { REPOSITORY_ROLE, authorisedRoles } from '../../types/generic/authRole';
import useRole from '../../helpers/hooks/useRole';
import DocumentSearchResultsPage from '../documentSearchResultsPage/DocumentSearchResultsPage';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

const mockedUseNavigate = jest.fn();
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useRole');
jest.mock('axios');
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
    useLocation: () => jest.fn(),
}));
jest.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});
const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedUseRole = useRole as jest.Mock;

describe('PatientSearchPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it.each(authorisedRoles)(
            "renders the page with patient search form when user role is '%s'",
            async (role) => {
                mockedUseRole.mockReturnValue(role);

                renderPatientSearchPage();
                expect(screen.getByText('Search for patient')).toBeInTheDocument();
                expect(
                    screen.getByRole('textbox', { name: 'Enter NHS number' }),
                ).toBeInTheDocument();
                expect(
                    screen.getByText('A 10-digit number, for example, 485 777 3456'),
                ).toBeInTheDocument();
                expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
            },
        );
        it.each(authorisedRoles)(
            "displays a loading spinner when the patients details are being requested when user role is '%s'",
            async (role) => {
                mockedUseRole.mockReturnValue(role);

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

                userEvent.type(
                    screen.getByRole('textbox', { name: 'Enter NHS number' }),
                    '9000000009',
                );
                userEvent.click(screen.getByRole('button', { name: 'Search' }));

                await waitFor(() => {
                    expect(screen.getByRole('button')).toBeInTheDocument();
                });
            },
        );

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
                    data: { message: '500 Unknown Service Error.', err_code: 'test' },
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

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            renderPatientSearchPage();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates to download journey when role is PCSE', async () => {
            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: buildPatientDetails() }),
            );
            const role = REPOSITORY_ROLE.PCSE;
            mockedUseRole.mockReturnValue(role);

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000000');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.VERIFY_PATIENT);
            });
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "navigates to upload journey when role is '%s'",
            async (role) => {
                mockedAxios.get.mockImplementation(() =>
                    Promise.resolve({ data: buildPatientDetails() }),
                );
                mockedUseRole.mockReturnValue(role);
                renderPatientSearchPage();
                userEvent.type(
                    screen.getByRole('textbox', { name: 'Enter NHS number' }),
                    '9000000000',
                );
                userEvent.click(screen.getByRole('button', { name: 'Search' }));

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.VERIFY_PATIENT);
                });
            },
        );

        it('navigates to session expired page page when user is unauthorized to make request', async () => {
            const errorResponse = {
                response: {
                    status: 403,
                    message: '403 Unauthorized.',
                },
            };

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000000');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });

        it('navigates to server error page when API returns 5XX', async () => {
            const errorResponse = {
                response: {
                    status: 500,
                    data: { message: '500 Unknown Service Error.', err_code: 'test' },
                },
            };

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000000');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routes.SERVER_ERROR + '?encodedError=WyJ0ZXN0IiwiMTU3NzgzNjgwMCJd',
                );
            });
        });
    });

    describe('Validation', () => {
        it('allows NHS number with spaces to be submitted', async () => {
            const testNumber = '900 000 0000';

            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: buildPatientDetails() }),
            );

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), testNumber);
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.VERIFY_PATIENT);
            });
        });

        it('allows NHS number with dashes to be submitted', async () => {
            const testNumber = '900-000-0000';

            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: buildPatientDetails() }),
            );

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), testNumber);
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.VERIFY_PATIENT);
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

const renderPatientSearchPage = () => {
    const patient: PatientDetails = buildPatientDetails();
    render(
        <PatientDetailsProvider patientDetails={patient}>
            <PatientSearchPage />
        </PatientDetailsProvider>,
    );
};
