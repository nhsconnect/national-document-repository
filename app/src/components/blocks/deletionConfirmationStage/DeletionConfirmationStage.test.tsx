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
import usePatient from '../../../helpers/hooks/usePatient';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';

const mockedUseNavigate = jest.fn();
const mockNavigate = jest.fn();

jest.mock('../../../helpers/hooks/useRole');
jest.mock('../../../helpers/hooks/usePatient');
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));

jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));

const mockedUseRole = useRole as jest.Mock;
const mockedUsePatient = usePatient as jest.Mock;

const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();
const mockSetStage = jest.fn();
const mockSetDownloadStage = jest.fn();

describe('DeletionConfirmationStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatientDetails);
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
                        setStage={mockSetStage}
                    />,
                );

                await waitFor(async () => {
                    expect(screen.getByText('Deletion complete')).toBeInTheDocument();
                });

                expect(
                    screen.getByText(
                        `You have successfully deleted ${numberOfFiles} file(s) from the Lloyd George record of:`,
                    ),
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
                <DeletionConfirmationStage numberOfFiles={numberOfFiles} setStage={mockSetStage} />,
            );

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            expect(
                screen.queryByText(
                    `You have successfully deleted ${numberOfFiles} file(s) from the Lloyd George record of:`,
                ),
            ).not.toBeInTheDocument();
            expect(
                screen.getByText(
                    `You have successfully deleted ${numberOfFiles} file(s) from the record of:`,
                ),
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
                <DeletionConfirmationStage numberOfFiles={numberOfFiles} setStage={mockSetStage} />,
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
                <DeletionConfirmationStage numberOfFiles={numberOfFiles} setStage={mockSetStage} />,
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
    });

    describe('Navigation', () => {
        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "navigates to the Lloyd George view page when return button is clicked, when user role is '%s'",
            async (role) => {
                const numberOfFiles = mockLgSearchResult.number_of_files;
                mockedUseRole.mockReturnValue(role);

                render(
                    <DeletionConfirmationStage
                        numberOfFiles={numberOfFiles}
                        setStage={mockSetStage}
                        setDownloadStage={mockSetDownloadStage}
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
                    expect(mockNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
                });
                expect(mockSetDownloadStage).toHaveBeenCalledWith(DOWNLOAD_STAGE.REFRESH);
            },
        );

        it('navigates to Home page when link is clicked when user role is PCSE', async () => {
            const numberOfFiles = 7;
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            render(
                <DeletionConfirmationStage numberOfFiles={numberOfFiles} setStage={mockSetStage} />,
            );

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            act(() => {
                userEvent.click(screen.getByRole('link'));
            });

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith(routes.START);
            });
        });
    });
});
