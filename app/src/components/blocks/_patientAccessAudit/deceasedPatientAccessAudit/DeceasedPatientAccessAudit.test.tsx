import DeceasedPatientAccessAudit from './DeceasedPatientAccessAudit';
import { render, screen, waitFor } from '@testing-library/react';
import { LinkProps, MemoryRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';
import {
    buildPatientAccessAudit,
    buildPatientDetails,
} from '../../../../helpers/test/testBuilders';
import {
    DeceasedAccessAuditReasons,
    PatientAccessAudit,
} from '../../../../types/generic/accessAudit';
import useRole from '../../../../helpers/hooks/useRole';
import usePatient from '../../../../helpers/hooks/usePatient';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import PatientAccessAuditProvider from '../../../../providers/patientAccessAuditProvider/PatientAccessAuditProvider';
import ConfigProvider from '../../../../providers/configProvider/ConfigProvider';
import PatientDetailsProvider from '../../../../providers/patientProvider/PatientProvider';
import { beforeEach, describe, expect, it, vi, Mock } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', async () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    ...(await vi.importActual('react-router-dom')),
    useNavigate: () => mockedUseNavigate,
}));
vi.mock('../../../../helpers/hooks/useRole');
vi.mock('../../../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('../../../../helpers/requests/postPatientAccessAudit', () => ({
    default: vi.fn().mockReturnValue({ response: { status: 200 } }),
}));

const mockedUseRole = useRole as Mock;
const mockedUsePatient = usePatient as Mock;

describe('DeceasedPatientAccessAudit', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });

    describe('Rendering', () => {
        const mockPatientDetails = buildPatientDetails();

        beforeEach(() => {
            mockedUsePatient.mockReturnValue(mockPatientDetails);
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
        });

        it('should render the page correctly', async () => {
            renderDeceasedPatientAccessAudit();

            const title = screen.getByTestId('title');
            expect(title).toBeInTheDocument();
            expect(title.innerHTML).toContain('Deceased patient record');
            expect(screen.getByTestId('patient-nhs-number')).toBeInTheDocument();
            expect(screen.queryByTestId('access-reason-error-box')).not.toBeInTheDocument();

            Object.values(DeceasedAccessAuditReasons).forEach((reason) => {
                const checkbox: HTMLInputElement = screen.getByTestId(`reason-checkbox-${reason}`);
                expect(checkbox.value).toBe(reason);
            });
        });

        it('should render error notification when no reason is selected', async () => {
            renderDeceasedPatientAccessAudit();

            await userEvent.click(screen.getByTestId('form-submit-button'));

            await waitFor(() => {
                const errorBox = screen.getByTestId('access-reason-error-box');
                expect(errorBox.innerHTML).toContain(
                    'Select a reason why you need to access this record',
                );
            });
        });

        it('should render error notification when another reason is selected and no reason is entered', async () => {
            renderDeceasedPatientAccessAudit();

            await userEvent.click(
                screen.getByTestId(`reason-checkbox-${DeceasedAccessAuditReasons.anotherReason}`),
            );
            await userEvent.click(screen.getByTestId('form-submit-button'));

            await waitFor(() => {
                const errorBox = screen.getByTestId('access-reason-error-box');
                expect(errorBox.innerHTML).toContain(
                    'Enter a reason why you need to access this record',
                );
            });
        });

        it('should render error notification when a reason and another reason is selected and no reason is entered', async () => {
            renderDeceasedPatientAccessAudit();

            await userEvent.click(
                screen.getByTestId(`reason-checkbox-${DeceasedAccessAuditReasons.familyRequest}`),
            );
            await userEvent.click(
                screen.getByTestId(`reason-checkbox-${DeceasedAccessAuditReasons.anotherReason}`),
            );
            await userEvent.click(screen.getByTestId('form-submit-button'));

            await waitFor(() => {
                const errorBox = screen.getByTestId('access-reason-error-box');
                expect(errorBox.innerHTML).toContain(
                    'Enter a reason why you need to access this record',
                );
            });
        });
    });

    describe('Navigation', () => {
        it('should navigate to the patient search page if there is no patient in the context', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            mockedUsePatient.mockReturnValue(undefined);
            renderDeceasedPatientAccessAudit();

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
            });
        });

        it('should navigate to Lloyd George when a reason is selected for active patient', async () => {
            const mockPatientDetails = buildPatientDetails();
            mockedUsePatient.mockReturnValue(mockPatientDetails);
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            renderDeceasedPatientAccessAudit();

            await userEvent.click(
                screen.getByTestId(`reason-checkbox-${DeceasedAccessAuditReasons.familyRequest}`),
            );
            await userEvent.click(screen.getByTestId('form-submit-button'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
            });
        });

        it('should navigate to Lloyd George when another reason is selected for active patient', async () => {
            const mockPatientDetails = buildPatientDetails();
            mockedUsePatient.mockReturnValue(mockPatientDetails);
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            renderDeceasedPatientAccessAudit();

            await userEvent.click(
                screen.getByTestId(`reason-checkbox-${DeceasedAccessAuditReasons.anotherReason}`),
            );
            await userEvent.type(screen.getByTestId('otherReasonText'), 'reason');
            await userEvent.click(screen.getByTestId('form-submit-button'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
            });
        });
    });
});

const renderDeceasedPatientAccessAudit = () => {
    const patientAccessAudit: PatientAccessAudit[] = buildPatientAccessAudit();

    render(
        <ConfigProvider>
            <PatientDetailsProvider>
                <PatientAccessAuditProvider patientAccessAudit={patientAccessAudit}>
                    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                        <DeceasedPatientAccessAudit />
                    </MemoryRouter>
                </PatientAccessAuditProvider>
            </PatientDetailsProvider>
        </ConfigProvider>,
    );
};
