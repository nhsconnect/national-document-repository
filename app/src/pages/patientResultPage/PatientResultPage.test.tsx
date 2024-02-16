import { render, screen, waitFor } from '@testing-library/react';
import PatientResultPage from './PatientResultPage';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import { routes } from '../../types/generic/routes';
import { act } from 'react-dom/test-utils';
import { REPOSITORY_ROLE, authorisedRoles } from '../../types/generic/authRole';
import useRole from '../../helpers/hooks/useRole';
import usePatient from '../../helpers/hooks/usePatient';

const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
    useLocation: () => jest.fn(),
}));
jest.mock('../../helpers/hooks/useRole');
jest.mock('../../helpers/hooks/usePatient');

const mockedUseRole = useRole as jest.Mock;
const mockedUsePatient = usePatient as jest.Mock;

describe('PatientResultPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('displays component', () => {
            render(<PatientResultPage />);

            expect(screen.getByText('Verify patient details')).toBeInTheDocument();
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

                expect(
                    screen.getByRole('heading', { name: 'Verify patient details' }),
                ).toBeInTheDocument();
                expect(screen.getByText(familyName)).toBeInTheDocument();
                expect(
                    screen.getByRole('button', { name: 'Accept details are correct' }),
                ).toBeInTheDocument();
                expect(screen.getByText(/If patient details are incorrect/)).toBeInTheDocument();

                const nationalServiceDeskLink = screen.getByRole('link', {
                    name: /National Service Desk/,
                });

                expect(nationalServiceDeskLink).toHaveAttribute(
                    'href',
                    'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
                );
                expect(nationalServiceDeskLink).toHaveAttribute('target', '_blank');
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

                expect(
                    screen.getByRole('heading', { name: 'Verify patient details' }),
                ).toBeInTheDocument();
                expect(
                    screen.getByText(
                        'Check these patient details match the records or attachments you plan to use',
                    ),
                ).toBeInTheDocument();
            },
        );

        it("doesn't display text specific to upload path when user role is PCSE", async () => {
            const nhsNumber = '9000000000';
            const patientDetails = buildPatientDetails({ nhsNumber });

            const role = REPOSITORY_ROLE.PCSE;
            mockedUseRole.mockReturnValue(role);
            mockedUsePatient.mockReturnValue(patientDetails);

            render(<PatientResultPage />);

            expect(
                screen.getByRole('heading', { name: 'Verify patient details' }),
            ).toBeInTheDocument();

            expect(screen.queryByText('Select patient status')).not.toBeInTheDocument();
            expect(screen.queryByRole('radio', { name: 'Active patient' })).not.toBeInTheDocument();
            expect(
                screen.queryByRole('radio', { name: 'Inactive patient' }),
            ).not.toBeInTheDocument();
            expect(
                screen.queryByText(
                    'Check these patient details match the records or attachments you plan to use',
                ),
            ).not.toBeInTheDocument();
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "displays an error message if 'active' boolean is missing on the patient, when role is '%s'",
            async (role) => {
                const patient = buildPatientDetails({ active: undefined });
                mockedUseRole.mockReturnValue(role);
                mockedUsePatient.mockReturnValue(patient);

                render(<PatientResultPage />);

                act(() => {
                    userEvent.click(
                        screen.getByRole('button', {
                            name: 'Accept details are correct',
                        }),
                    );
                });

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

            expect(
                screen.getByRole('heading', { name: 'Verify patient details' }),
            ).toBeInTheDocument();
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

            expect(
                screen.getByRole('heading', { name: 'Verify patient details' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(
                    'Certain details about this patient cannot be displayed without the necessary access.',
                ),
            ).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "navigates to Upload docs page after user selects Inactive patient when role is '%s'",
            async (role) => {
                const patient = buildPatientDetails({ active: false });

                mockedUsePatient.mockReturnValue(patient);
                mockedUseRole.mockReturnValue(role);
                render(<PatientResultPage />);
                act(() => {
                    userEvent.click(
                        screen.getByRole('button', {
                            name: 'Accept details are correct',
                        }),
                    );
                });

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.ARF_UPLOAD_DOCUMENTS);
                });
            },
        );

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "navigates to Lloyd George Record page after user selects Active patient, when role is '%s'",
            async (role) => {
                const patient = buildPatientDetails({ active: true });
                mockedUseRole.mockReturnValue(role);
                mockedUsePatient.mockReturnValue(patient);

                render(<PatientResultPage />);

                act(() => {
                    userEvent.click(
                        screen.getByRole('button', { name: 'Accept details are correct' }),
                    );
                });

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
                });
            },
        );

        it('navigates to ARF Download page when user selects Verify patient, when role is PCSE', async () => {
            const role = REPOSITORY_ROLE.PCSE;
            mockedUseRole.mockReturnValue(role);

            render(<PatientResultPage />);

            userEvent.click(screen.getByRole('button', { name: 'Accept details are correct' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.ARF_DOWNLOAD_DOCUMENTS);
            });
        });
    });
});
