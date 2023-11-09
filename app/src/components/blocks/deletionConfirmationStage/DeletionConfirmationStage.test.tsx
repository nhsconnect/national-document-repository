import { render, screen, waitFor } from '@testing-library/react';
import { buildLgSearchResult, buildPatientDetails } from '../../../helpers/test/testBuilders';
import DeletionConfirmationStage from './DeletionConfirmationStage';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import { routes } from '../../../types/generic/routes';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';

jest.mock('../../../helpers/hooks/useRole');
const mockedUseRole = useRole as jest.Mock;

const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();
const mockSetStage = jest.fn();

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
                renderComponent(numberOfFiles);

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
            renderComponent(numberOfFiles);

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            expect(
                screen.getByText(`${numberOfFiles} file from the record of:`),
            ).toBeInTheDocument();
            expect(screen.getByText(patientName)).toBeInTheDocument();
            expect(screen.getByText(/NHS number/)).toBeInTheDocument();
            expect(
                screen.getByRole('link', {
                    name: 'Start Again',
                }),
            ).toBeInTheDocument();
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "renders the return to Lloyd George Record button, when user role is '%s'",
            async (role) => {
                const numberOfFiles = mockLgSearchResult.number_of_files;
                mockedUseRole.mockReturnValue(role);

                renderComponent(numberOfFiles);

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

            renderComponent(numberOfFiles);

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

            renderComponent(numberOfFiles);

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

                renderComponent(numberOfFiles);

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

                renderComponent(numberOfFiles);

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
            const history = createMemoryHistory({
                initialEntries: ['/'],
                initialIndex: 0,
            });

            const numberOfFiles = 7;
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            renderComponent(numberOfFiles, history);

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            act(() => {
                userEvent.click(
                    screen.getByRole('link', {
                        name: 'Start Again',
                    }),
                );
            });

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.HOME);
            });
        });
    });
});

const renderComponent = (
    numberOfFiles: number,
    history = createMemoryHistory({
        initialEntries: ['/'],
        initialIndex: 0,
    }),
) => {
    render(
        <ReactRouter.Router navigator={history} location={'/'}>
            <DeletionConfirmationStage
                numberOfFiles={numberOfFiles}
                patientDetails={mockPatientDetails}
                setStage={mockSetStage}
            />
        </ReactRouter.Router>,
    );
};
