import { render, screen, waitFor } from '@testing-library/react';
import HomePage from './HomePage';
import useIsBSOL from '../../helpers/hooks/useIsBSOL';
import useRole from '../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { routes } from '../../types/generic/routes';

const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));

jest.mock('../../helpers/hooks/useIsBSOL');
const mockUseIsBsol = useIsBSOL as jest.Mock;

jest.mock('../../helpers/hooks/useRole');
const mockUseRole = useRole as jest.Mock;

describe('HomePage', () => {
    describe('User is BSOL', () => {
        beforeEach(() => {
            mockUseIsBsol.mockReturnValue(true);
        });
        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "renders homepage content when user role is '%s'",
            async (role) => {
                mockUseRole.mockReturnValue(role);
                const mockNavigate = jest.fn();
                const mockUseNavigate = jest.fn();
                mockNavigate.mockImplementation(() => mockUseNavigate);

                const contentStrings = [
                    'This service gives you access to Lloyd George digital health records. ' +
                        'You may have received a note within a patient record, stating that the record has been digitised.',
                    'If you are part of a GP practice, you can use this service to:',
                    'view a patient record',
                    'remove a patient record',
                    'If you are managing records on behalf of NHS England, you can:',
                    'Not every patient will have a digital record available.',
                    'Before you start',
                    'You’ll be asked for:',
                    'your NHS smartcard',
                    'patient details including their name, date of birth and NHS number',
                ];

                render(<HomePage />);

                contentStrings.forEach((s) => {
                    expect(screen.getByText(s)).toBeInTheDocument();
                });

                const downloadPatientRecord = screen.getAllByText('download a patient record');
                expect(downloadPatientRecord).toHaveLength(2);

                expect(screen.getByText(/Contact the/i)).toBeInTheDocument();
                expect(
                    screen.getByRole('link', {
                        name: /NHS National Service Desk/i,
                    }),
                ).toBeInTheDocument();
                expect(
                    screen.getByText(
                        /if there is an issue with this service or call 0300 303 5678\./i,
                    ),
                ).toBeInTheDocument();

                expect(screen.getByTestId('search-patient-btn')).toBeInTheDocument();
            },
        );

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "renders a service link that takes you to service help-desk in a new tab when user role is '%s'",
            async (role) => {
                mockUseRole.mockReturnValue(role);
                render(<HomePage />);

                expect(screen.getByText(/Contact the/i)).toBeInTheDocument();
                const nationalServiceDeskLink = screen.getByRole('link', {
                    name: /NHS National Service Desk/i,
                });
                expect(
                    screen.getByText(
                        /if there is an issue with this service or call 0300 303 5678/i,
                    ),
                ).toBeInTheDocument();

                expect(nationalServiceDeskLink).toHaveAttribute(
                    'href',
                    'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
                );
                expect(nationalServiceDeskLink).toHaveAttribute('target', '_blank');
            },
        );

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "navigates to correct search page when user role is '%s'",
            async (role) => {
                mockUseRole.mockReturnValue(role);
                render(<HomePage />);

                expect(screen.getByTestId('search-patient-btn')).toBeInTheDocument();
                screen.getByTestId('search-patient-btn').click();
                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UPLOAD_SEARCH);
                });
            },
        );
    });

    describe('User is non-BSOL', () => {});
});
