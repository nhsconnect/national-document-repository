import { act, render, screen, waitFor } from '@testing-library/react';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { PatientDetails } from '../../types/generic/patientDetails';
import PatientSearchPage, { incorrectFormatMessage } from './PatientSearchPage';
import userEvent from '@testing-library/user-event';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import axios from 'axios';
import { routes } from '../../types/generic/routes';
import { REPOSITORY_ROLE, authorisedRoles } from '../../types/generic/authRole';
import useRole from '../../helpers/hooks/useRole';
import ConfigProvider from '../../providers/configProvider/ConfigProvider';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import waitForSeconds from '../../helpers/utils/waitForSeconds';
import { afterEach, beforeEach, describe, expect, it, vi, Mock, Mocked } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../helpers/hooks/useRole');
vi.mock('axios');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
    useLocation: () => vi.fn(),
}));
vi.mock('../../helpers/hooks/useConfig', () => ({
    default: () => ({
        featureFlags: {
            uploadArfWorkflowEnabled: false,
        },
    }),
}));

Date.now = () => new Date('2020-01-01T00:00:00.000Z').getTime();
const mockedAxios = axios as Mocked<typeof axios>;
const mockedUseRole = useRole as Mock;

describe('PatientSearchPage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it.each(authorisedRoles)(
            "renders the page with patient search form when user role is '%s'",
            async (role) => {
                mockedUseRole.mockReturnValue(role);

                renderPatientSearchPage();
                expect(screen.getByText('Search for a patient')).toBeInTheDocument();
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

                mockedAxios.get.mockImplementation(() => waitForSeconds(1));

                renderPatientSearchPage();

                userEvent.type(
                    screen.getByRole('textbox', { name: 'Enter NHS number' }),
                    '9000000009',
                );
                userEvent.click(screen.getByRole('button', { name: 'Search' }));

                expect(
                    await screen.findByRole('button', { name: 'Searching...' }),
                ).toBeInTheDocument();
            },
        );

        it('displays an input error when user attempts to submit an invalid NHS number', async () => {
            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '21212');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            await waitFor(() => {
                expect(screen.getAllByText(incorrectFormatMessage)).toHaveLength(2);
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
                    data: {
                        err_code: 'SP_4002',
                    },
                },
            };

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '0987654321');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            expect(
                await screen.findAllByText(
                    'The NHS number entered could not be found in the Personal Demographics Service',
                ),
            ).toHaveLength(2);
        });

        it('returns an input error when user does not have access to patient data', async () => {
            const errorResponse = {
                response: {
                    status: 404,
                    message: '404 Not found.',
                    data: {
                        err_code: 'SP_4003',
                    },
                },
            };

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '0987654321');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            expect(
                await screen.findAllByText(
                    "You cannot access this patient's record because they are not registered at your practice. The patient's current practice can access this record.",
                ),
            ).toHaveLength(2);
        });

        it('returns patient info when patient is inactive and deceased', async () => {
            const patientDetails = buildPatientDetails({
                active: false,
                deceased: true,
            });

            mockedAxios.get.mockImplementation(() => Promise.resolve({ data: patientDetails }));

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000000');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.VERIFY_PATIENT);
            });
        });

        it('returns an error when patient is inactive and not deceased and user is clinical', async () => {
            const patientDetails = buildPatientDetails({
                active: false,
                deceased: false,
            });

            mockedAxios.get.mockImplementation(() => Promise.resolve({ data: patientDetails }));

            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000000');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            expect(
                await screen.findAllByText(
                    "You cannot access this patient's record because they are not registered at your practice. The patient's current practice can access this record.",
                ),
            ).toHaveLength(2);
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

        it('pass accessibility checks when ErrorBox appears', async () => {
            const errorResponse = {
                response: {
                    status: 404,
                    message: '404 Not found.',
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPatientSearchPage();
            act(() => {
                userEvent.type(
                    screen.getByRole('textbox', { name: 'Enter NHS number' }),
                    '0987654321',
                );
                userEvent.click(screen.getByRole('button', { name: 'Search' }));
            });
            await screen.findByText('There is a problem');

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

        it.each([REPOSITORY_ROLE.GP_ADMIN])(
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

        it('display input error when patient is inactive and upload feature is disabled', async () => {
            const role = REPOSITORY_ROLE.GP_ADMIN;
            mockedUseRole.mockReturnValue(role);
            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: { ...buildPatientDetails(), active: false } }),
            );

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '0987654321');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            expect(
                await screen.findAllByText(
                    "You cannot access this patient's record because they are not registered at your practice. The patient's current practice can access this record.",
                ),
            ).toHaveLength(2);
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

        it('allows NHS number with spaces at beginning and end to be submitted', async () => {
            const testNumber = '  9000000000 ';

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

        it('allows NHS number with spaces to be submitted and spaces at the end', async () => {
            const testNumber = '900 000 0000  ';

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

        it('allows NHS number with dashes to be submitted and spaces at the end', async () => {
            const testNumber = '900-000-0000 ';

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
                expect(screen.getAllByText(incorrectFormatMessage)).toHaveLength(2);
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
                    expect(screen.getAllByText(incorrectFormatMessage)).toHaveLength(2);
                });
            },
        );

        it('a defined width class is applied to the NHS number input field', async () => {
            const definedWidthClass = 'nhsuk-input--width-10';

            renderPatientSearchPage();

            const input = screen.getByTestId('nhs-number-input');
            expect(input).toHaveClass(definedWidthClass);
        });
    });
});

const renderPatientSearchPage = () => {
    const patient: PatientDetails = buildPatientDetails();
    render(
        <ConfigProvider>
            <PatientDetailsProvider patientDetails={patient}>
                <PatientSearchPage />
            </PatientDetailsProvider>
        </ConfigProvider>,
    );
};
