import { render, screen, waitFor } from '@testing-library/react';
import { buildLgSearchResult, buildPatientDetails } from '../../../helpers/test/testBuilders';
import DeletionConfirmationStage from './DeletionConfirmationStage';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../types/generic/routes';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import { LinkProps } from 'react-router-dom';

jest.mock('../../../helpers/hooks/useRole');
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));

const mockedUseRole = useRole as jest.Mock;
const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();
const mockSetStage = jest.fn();
const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('DeletionConfirmationStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "renders the page with Lloyd George patient details when user role is '%s'",
            async (role) => {
                const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
                const numberOfFiles = mockLgSearchResult.number_of_files;

                mockedUseRole.mockReturnValue(role);
                render(
                    <DeletionConfirmationStage
                        numberOfFiles={numberOfFiles}
                        patientDetails={mockPatientDetails}
                        setStage={mockSetStage}
                    />,
                );

                await waitFor(async () => {
                    expect(screen.getByText('Deletion complete')).toBeInTheDocument();
                });

                expect(
                    screen.getByText(`${numberOfFiles} files from the Lloyd George record of:`),
                ).toBeInTheDocument();
                expect(screen.getByText(patientName)).toBeInTheDocument();
                expect(screen.getByText(/NHS number/)).toBeInTheDocument();
                expect(
                    screen.getByRole('button', {
                        name: "Return to patient's Lloyd George record page",
                    }),
                ).toBeInTheDocument();
            },
        );
        it('renders the page with ARF patient details, when user role is PCSE', async () => {
            const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
            const numberOfFiles = 1;

            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
            render(
                <DeletionConfirmationStage
                    numberOfFiles={numberOfFiles}
                    patientDetails={mockPatientDetails}
                    setStage={mockSetStage}
                />,
            );

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            expect(
                screen.queryByText(`${numberOfFiles} files from the Lloyd George record of:`),
            ).not.toBeInTheDocument();
            expect(
                screen.getByText(`${numberOfFiles} file from the record of:`),
            ).toBeInTheDocument();
            expect(screen.getByText(patientName)).toBeInTheDocument();
            expect(screen.getByText(/NHS number/)).toBeInTheDocument();
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "renders the return to Lloyd George Record button, when user role is '%s'",
            async (role) => {
                const numberOfFiles = mockLgSearchResult.number_of_files;
                mockedUseRole.mockReturnValue(role);

                render(
                    <DeletionConfirmationStage
                        numberOfFiles={numberOfFiles}
                        patientDetails={mockPatientDetails}
                        setStage={mockSetStage}
                    />,
                );

                await waitFor(async () => {
                    expect(screen.getByText('Deletion complete')).toBeInTheDocument();
                });

                expect(
                    screen.getByRole('button', {
                        name: "Return to patient's Lloyd George record page",
                    }),
                ).toBeInTheDocument();
            },
        );

        it('does not render the return to Lloyd George Record button, when user role is PCSE', async () => {
            const numberOfFiles = mockLgSearchResult.number_of_files;
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            render(
                <DeletionConfirmationStage
                    numberOfFiles={numberOfFiles}
                    patientDetails={mockPatientDetails}
                    setStage={mockSetStage}
                />,
            );

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            expect(
                screen.queryByRole('button', {
                    name: "Return to patient's Lloyd George record page",
                }),
            ).not.toBeInTheDocument();
        });

        it('renders the Start Again button, when user role is PCSE', async () => {
            const numberOfFiles = 7;
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            render(
                <DeletionConfirmationStage
                    numberOfFiles={numberOfFiles}
                    patientDetails={mockPatientDetails}
                    setStage={mockSetStage}
                />,
            );

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            expect(
                screen.getByRole('link', {
                    name: 'Start Again',
                }),
            ).toBeInTheDocument();
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "does not render the Start Again button, when user role is '%s'",
            async (role) => {
                const numberOfFiles = 7;
                mockedUseRole.mockReturnValue(role);

                render(
                    <DeletionConfirmationStage
                        numberOfFiles={numberOfFiles}
                        patientDetails={mockPatientDetails}
                        setStage={mockSetStage}
                    />,
                );

                await waitFor(async () => {
                    expect(screen.getByText('Deletion complete')).toBeInTheDocument();
                });

                expect(
                    screen.queryByRole('link', {
                        name: 'Start Again',
                    }),
                ).not.toBeInTheDocument();
            },
        );

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "displays the LgRecordStage when return button is clicked, when user role is '%s'",
            async (role) => {
                const numberOfFiles = mockLgSearchResult.number_of_files;
                mockedUseRole.mockReturnValue(role);

                render(
                    <DeletionConfirmationStage
                        numberOfFiles={numberOfFiles}
                        patientDetails={mockPatientDetails}
                        setStage={mockSetStage}
                    />,
                );

                await waitFor(async () => {
                    expect(screen.getByText('Deletion complete')).toBeInTheDocument();
                });

                act(() => {
                    userEvent.click(
                        screen.getByRole('button', {
                            name: "Return to patient's Lloyd George record page",
                        }),
                    );
                });

                await waitFor(() => {
                    expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
                });
            },
        );
    });

    describe('Navigation', () => {
        it('navigates to Home page when link is clicked when user role is PCSE', async () => {
            const numberOfFiles = 7;
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            render(
                <DeletionConfirmationStage
                    numberOfFiles={numberOfFiles}
                    patientDetails={mockPatientDetails}
                    setStage={mockSetStage}
                />,
            );

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            act(() => {
                userEvent.click(screen.getByRole('link'));
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
            });
        });
    });
});
