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
import { act } from 'react-dom/test-utils';
import useRole from '../../../../helpers/hooks/useRole';
import usePatient from '../../../../helpers/hooks/usePatient';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import PatientAccessAuditProvider from '../../../../providers/patientAccessAuditProvider/PatientAccessAuditProvider';
import ConfigProvider from '../../../../providers/configProvider/ConfigProvider';
import PatientDetailsProvider from '../../../../providers/patientProvider/PatientProvider';

const mockedUseNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('../../../../helpers/hooks/useRole');
jest.mock('../../../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../../helpers/hooks/usePatient');
jest.mock('../../../../helpers/requests/postPatientAccessAudit', () => {
    return () => {
        return { response: { status: 200 } };
    };
});

const mockedUseRole = useRole as jest.Mock;
const mockedUsePatient = usePatient as jest.Mock;

describe('DeceasedPatientAccessAudit', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
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

            act(() => {
                userEvent.click(screen.getByTestId('form-submit-button'));
            });

            await waitFor(() => {
                const errorBox = screen.getByTestId('access-reason-error-box');
                expect(errorBox.innerHTML).toContain(
                    'Select a reason why you need to access this record',
                );
            });
        });

        it('should render error notification when another reason is selected and no reason is entered', async () => {
            renderDeceasedPatientAccessAudit();

            act(() => {
                userEvent.click(
                    screen.getByTestId(
                        `reason-checkbox-${DeceasedAccessAuditReasons.anotherReason}`,
                    ),
                );
                userEvent.click(screen.getByTestId('form-submit-button'));
            });

            await waitFor(() => {
                const errorBox = screen.getByTestId('access-reason-error-box');
                expect(errorBox.innerHTML).toContain(
                    'Enter a reason why you need to access this record',
                );
            });
        });

        it('should render error notification when a reason and another reason is selected and no reason is entered', async () => {
            renderDeceasedPatientAccessAudit();

            act(() => {
                userEvent.click(
                    screen.getByTestId(
                        `reason-checkbox-${DeceasedAccessAuditReasons.familyRequest}`,
                    ),
                );
                userEvent.click(
                    screen.getByTestId(
                        `reason-checkbox-${DeceasedAccessAuditReasons.anotherReason}`,
                    ),
                );
                userEvent.click(screen.getByTestId('form-submit-button'));
            });

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

            act(() => {
                userEvent.click(
                    screen.getByTestId(
                        `reason-checkbox-${DeceasedAccessAuditReasons.familyRequest}`,
                    ),
                );
                userEvent.click(screen.getByTestId('form-submit-button'));
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
            });
        });

        it('should navigate to Lloyd George when another reason is selected for active patient', async () => {
            const mockPatientDetails = buildPatientDetails();
            mockedUsePatient.mockReturnValue(mockPatientDetails);
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            renderDeceasedPatientAccessAudit();

            act(() => {
                userEvent.click(
                    screen.getByTestId(
                        `reason-checkbox-${DeceasedAccessAuditReasons.anotherReason}`,
                    ),
                );
                userEvent.type(screen.getByTestId('otherReasonText'), 'reason');
                userEvent.click(screen.getByTestId('form-submit-button'));
            });

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
                    <MemoryRouter>
                        <DeceasedPatientAccessAudit />
                    </MemoryRouter>
                </PatientAccessAuditProvider>
            </PatientDetailsProvider>
        </ConfigProvider>,
    );
};
