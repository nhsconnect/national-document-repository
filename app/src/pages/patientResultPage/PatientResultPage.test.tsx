import { render, screen, waitFor } from '@testing-library/react';
import PatientResultPage from './PatientResultPage';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import { routeChildren, routes } from '../../types/generic/routes';
import { REPOSITORY_ROLE, authorisedRoles } from '../../types/generic/authRole';
import useRole from '../../helpers/hooks/useRole';
import usePatient from '../../helpers/hooks/usePatient';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
    useLocation: () => vi.fn(),
}));
vi.mock('../../helpers/hooks/useRole');
vi.mock('../../helpers/hooks/usePatient');

const mockedUseRole = useRole as Mock;
const mockedUsePatient = usePatient as Mock;

const PAGE_HEADER_TEXT = 'Patient details';
const PAGE_TEXT =
    'This page displays the current data recorded in the Personal Demographics Service for this patient.';
const CONFIRM_BUTTON_TEXT = 'Confirm patient details and continue';

describe('PatientResultPage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('displays component', () => {
            render(<PatientResultPage />);

            expect(screen.getByText(PAGE_HEADER_TEXT)).toBeInTheDocument();
        });

        it.each(authorisedRoles)(
            "displays the patient details page when patient data is found when user role is '%s'",
            async (role) => {
                const nhsNumber = '9000000000';
                const familyName = 'Smith';
                const patientDetails = buildPatientDetails({ familyName, nhsNumber });
                mockedUseRole.mockReturnValue(role);
                mockedUsePatient.mockReturnValue(patientDetails);

                render(<PatientResultPage />);

                expect(screen.getByRole('heading', { name: PAGE_HEADER_TEXT })).toBeInTheDocument();
                expect(screen.getByText(familyName)).toBeInTheDocument();
                expect(
                    screen.getByRole('button', { name: CONFIRM_BUTTON_TEXT }),
                ).toBeInTheDocument();
            },
        );

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "displays text specific to upload path when user role is '%s'",
            async (role) => {
                const nhsNumber = '9000000000';
                const patientDetails = buildPatientDetails({ nhsNumber });

                mockedUseRole.mockReturnValue(role);
                mockedUsePatient.mockReturnValue(patientDetails);

                render(<PatientResultPage />);

                expect(screen.getByRole('heading', { name: PAGE_HEADER_TEXT })).toBeInTheDocument();
                expect(screen.getByText(PAGE_TEXT)).toBeInTheDocument();
            },
        );

        it("doesn't display text specific to upload path when user role is PCSE", async () => {
            const nhsNumber = '9000000000';
            const patientDetails = buildPatientDetails({ nhsNumber });

            const role = REPOSITORY_ROLE.PCSE;
            mockedUseRole.mockReturnValue(role);
            mockedUsePatient.mockReturnValue(patientDetails);

            render(<PatientResultPage />);

            expect(screen.getByRole('heading', { name: PAGE_HEADER_TEXT })).toBeInTheDocument();

            expect(screen.queryByText('Select patient status')).not.toBeInTheDocument();
            expect(screen.queryByRole('radio', { name: 'Active patient' })).not.toBeInTheDocument();
            expect(
                screen.queryByRole('radio', { name: 'Inactive patient' }),
            ).not.toBeInTheDocument();
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "displays an error message if 'active' boolean is missing on the patient, when role is '%s'",
            async (role) => {
                const patient = buildPatientDetails({ active: undefined });
                mockedUseRole.mockReturnValue(role);
                mockedUsePatient.mockReturnValue(patient);

                render(<PatientResultPage />);

                await userEvent.click(
                    screen.getByRole('button', {
                        name: CONFIRM_BUTTON_TEXT,
                    }),
                );

                await waitFor(() => {
                    expect(
                        screen.getByText('We cannot determine the active state of this patient'),
                    ).toBeInTheDocument();
                });
            },
        );

        it('displays a message when NHS number is superseded', async () => {
            const nhsNumber = '9000000012';
            const patientDetails = buildPatientDetails({ superseded: true, nhsNumber });
            mockedUsePatient.mockReturnValue(patientDetails);

            render(<PatientResultPage />);

            expect(screen.getByRole('heading', { name: PAGE_HEADER_TEXT })).toBeInTheDocument();
            expect(
                screen.getByText('The NHS number for this patient has changed.'),
            ).toBeInTheDocument();
        });

        it('displays a message when patient is sensitive', async () => {
            const nhsNumber = '9124038456';
            const patientDetails = buildPatientDetails({
                nhsNumber,
                postalCode: null,
                restricted: true,
            });
            mockedUsePatient.mockReturnValue(patientDetails);

            render(<PatientResultPage />);

            expect(screen.getByRole('heading', { name: PAGE_HEADER_TEXT })).toBeInTheDocument();
            expect(
                screen.getByText(
                    'Certain details about this patient cannot be displayed without the necessary access.',
                ),
            ).toBeInTheDocument();
        });

        it('displays a message when NHS number is deceased as a GP User', async () => {
            const nhsNumber = '9000000012';
            const patientDetails = buildPatientDetails({ deceased: true, nhsNumber });
            mockedUsePatient.mockReturnValue(patientDetails);
            const role = REPOSITORY_ROLE.GP_ADMIN;
            mockedUseRole.mockReturnValue(role);

            render(<PatientResultPage />);

            expect(screen.getByRole('heading', { name: PAGE_HEADER_TEXT })).toBeInTheDocument();
            expect(
                screen.getByText(
                    'Access to the records of deceased patients is regulated under the Access to Health Records Act',
                    { exact: false },
                ),
            ).toBeInTheDocument();
        });

        it('displays a deceased patient tag for a deceased patient as a PCSE user', async () => {
            const nhsNumber = '9000000012';
            const patientDetails = buildPatientDetails({ deceased: true, nhsNumber });
            mockedUsePatient.mockReturnValue(patientDetails);
            const role = REPOSITORY_ROLE.PCSE;
            mockedUseRole.mockReturnValue(role);

            render(<PatientResultPage />);

            expect(screen.getByRole('heading', { name: PAGE_HEADER_TEXT })).toBeInTheDocument();
            expect(screen.getByTestId('deceased-patient-tag')).toBeInTheDocument();
        });
    });

    describe('Accessibility', () => {
        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL, REPOSITORY_ROLE.PCSE])(
            'pass accessibility checks, role: %s',
            async (role) => {
                const nhsNumber = '9000000000';
                const patientDetails = buildPatientDetails({ nhsNumber });

                mockedUseRole.mockReturnValue(role);
                mockedUsePatient.mockReturnValue(patientDetails);

                render(<PatientResultPage />);

                expect(screen.getByRole('heading', { name: PAGE_HEADER_TEXT })).toBeInTheDocument();

                const results = await runAxeTest(document.body);
                expect(results).toHaveNoViolations();
            },
        );

        it('pass accessibility checks when displaying superseded patient', async () => {
            const nhsNumber = '9000000012';
            const patientDetails = buildPatientDetails({ superseded: true, nhsNumber });
            mockedUsePatient.mockReturnValue(patientDetails);

            render(<PatientResultPage />);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when displaying sensitive patient', async () => {
            const nhsNumber = '9124038456';
            const patientDetails = buildPatientDetails({
                nhsNumber,
                postalCode: null,
                restricted: true,
            });
            mockedUsePatient.mockReturnValue(patientDetails);

            render(<PatientResultPage />);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates to Upload docs page after user selects Inactive patient when role is GP Admin', async () => {
            const patient = buildPatientDetails({ active: false });

            mockedUsePatient.mockReturnValue(patient);
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            render(<PatientResultPage />);
            await userEvent.click(
                screen.getByRole('button', {
                    name: CONFIRM_BUTTON_TEXT,
                }),
            );

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.ARF_UPLOAD_DOCUMENTS);
            });
        });

        it('navigates to patient search page after user selects Inactive patient when role is GP Clinical', async () => {
            const patient = buildPatientDetails({ active: false });

            mockedUsePatient.mockReturnValue(patient);
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
            render(<PatientResultPage />);
            await userEvent.click(
                screen.getByRole('button', {
                    name: CONFIRM_BUTTON_TEXT,
                }),
            );

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
            });
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "navigates to Lloyd George Record page after user selects Active patient, when role is '%s'",
            async (role) => {
                const patient = buildPatientDetails({ active: true });
                mockedUseRole.mockReturnValue(role);
                mockedUsePatient.mockReturnValue(patient);

                render(<PatientResultPage />);

                await userEvent.click(screen.getByRole('button', { name: CONFIRM_BUTTON_TEXT }));

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
                });
            },
        );

        it('navigates to ARF Download page when user selects Verify patient, when role is PCSE', async () => {
            const role = REPOSITORY_ROLE.PCSE;
            mockedUseRole.mockReturnValue(role);

            render(<PatientResultPage />);

            await userEvent.click(screen.getByRole('button', { name: CONFIRM_BUTTON_TEXT }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.ARF_OVERVIEW);
            });
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "navigates to Deceased Patient Access Audit page after user selects Deceased patient, when role is '%s'",
            async (role) => {
                const patient = buildPatientDetails({ deceased: true });
                mockedUseRole.mockReturnValue(role);
                mockedUsePatient.mockReturnValue(patient);

                render(<PatientResultPage />);

                await userEvent.click(screen.getByRole('button', { name: CONFIRM_BUTTON_TEXT }));

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        routeChildren.PATIENT_ACCESS_AUDIT_DECEASED,
                    );
                });
            },
        );
    });
});
