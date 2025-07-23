import { render, screen, waitFor } from '@testing-library/react';
import { buildLgSearchResult, buildPatientDetails } from '../../../../helpers/test/testBuilders';
import DeleteSubmitStage, { Props } from './DeleteSubmitStage';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import userEvent from '@testing-library/user-event';
import { DOCUMENT_TYPE } from '../../../../types/pages/UploadDocumentsPage/types';
import axios from 'axios';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE, authorisedRoles } from '../../../../types/generic/authRole';
import { routes, routeChildren } from '../../../../types/generic/routes';
import usePatient from '../../../../helpers/hooks/usePatient';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { MemoryHistory, createMemoryHistory } from 'history';
import * as ReactRouter from 'react-router-dom';
import waitForSeconds from '../../../../helpers/utils/waitForSeconds';
import { afterEach, beforeEach, describe, expect, it, vi, Mock, Mocked } from 'vitest';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';

vi.mock('../../../../helpers/hooks/useConfig');
vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../../../helpers/hooks/useRole');
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('axios');

const mockedUseNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockedUseNavigate,
    };
});
Date.now = () => new Date('2020-01-01T00:00:00.000Z').getTime();

let history: MemoryHistory = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

const mockedUseRole = useRole as Mock;
const mockedAxios = axios as Mocked<typeof axios>;
const mockedUsePatient = usePatient as Mock;
const mockResetDocState = vi.fn();
const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();

const mockSetStage = vi.fn();

describe('DeleteSubmitStage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        mockedUsePatient.mockReturnValue(mockPatientDetails);
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Render', () => {
        it.each(authorisedRoles)(
            "renders the page with patient details when user role is '%s'",
            async (role) => {
                const patientName = `${mockPatientDetails.familyName}, ${mockPatientDetails.givenName}`;
                const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));
                mockedUseRole.mockReturnValue(role);

                renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

                await waitFor(async () => {
                    expect(
                        screen.getByText(
                            'Are you sure you want to permanently remove this record?',
                        ),
                    ).toBeInTheDocument();
                });

                expect(screen.getByText(patientName)).toBeInTheDocument();
                expect(screen.getByText(dob)).toBeInTheDocument();
                expect(screen.getByText(/NHS number/)).toBeInTheDocument();
                const yesButton = screen.getByRole('radio', { name: 'Yes' });
                expect(yesButton).toBeInTheDocument();
                expect(yesButton).not.toBeChecked();
                const noButton = screen.getByRole('radio', { name: 'No' });
                expect(noButton).toBeInTheDocument();
                expect(noButton).not.toBeChecked();
                expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();
                expect(
                    screen.queryByText(
                        'Select whether you want to permanently delete these patient files',
                    ),
                ).not.toBeInTheDocument();
            },
        );

        it('renders DocumentSearchResults when No is selected and Continue clicked, when user role is GP Admin', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);
            const noButton = screen.getByRole('radio', { name: 'No' });

            expect(noButton).not.toBeChecked();

            await userEvent.click(noButton);
            expect(noButton).toBeChecked();
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            expect(screen.queryByTestId('delete-error-box')).not.toBeInTheDocument();

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
            });
        });

        it('renders DocumentSearchResults when No is selected and Continue clicked, when user role is PCSE', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            renderComponent(DOCUMENT_TYPE.ALL, history);

            await userEvent.click(screen.getByRole('radio', { name: 'No' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.ARF_OVERVIEW);
            });
        });

        it('does not render a view DocumentSearchResults when No is selected and Continue clicked, when user role is GP Clinical', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            await userEvent.click(screen.getByRole('radio', { name: 'No' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await waitFor(() => {
                expect(mockSetStage).toHaveBeenCalledTimes(0);
            });
        });

        it('renders DeletionConfirmationStage when the Yes is selected and Continue clicked, when user role is GP_ADMIN', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            mockedAxios.delete.mockReturnValue(Promise.resolve({ status: 200, data: 'Success' }));

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            await userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routeChildren.LLOYD_GEORGE_DELETE_COMPLETE,
                );
            });
        });

        it('calls resetDocState when the Yes is selected and Continue clicked', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            mockedAxios.delete.mockReturnValue(Promise.resolve({ status: 200, data: 'Success' }));

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            await userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await waitFor(() => {
                expect(mockResetDocState).toHaveBeenCalled();
            });
        });

        it('renders DeletionConfirmationStage when the Yes is selected and Continue clicked, when user role is PCSE', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            mockedAxios.delete.mockReturnValue(Promise.resolve({ status: 200, data: 'Success' }));

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            await userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routeChildren.ARF_DELETE_COMPLETE);
            });
        });

        it('does not render DeleteResultStage when the Yes is selected, Continue clicked, and user role is GP Clinical', async () => {
            mockedAxios.delete.mockReturnValue(Promise.resolve({ status: 200, data: 'Success' }));
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            await userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await waitFor(() => {
                expect(screen.queryByText('Deletion complete')).not.toBeInTheDocument();
            });
        });

        it('renders a service error when service is down', async () => {
            const errorResponse = {
                response: {
                    status: 500,
                    data: { message: 'Client Error', err_code: 'SP_1001' },
                },
            };
            mockedAxios.delete.mockImplementation(() => Promise.reject(errorResponse));
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
            renderComponent(DOCUMENT_TYPE.ALL, history);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            await userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await waitFor(() => {
                expect(
                    screen.getByText('Sorry, the service is currently unavailable.'),
                ).toBeInTheDocument();
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
                );
            });
        });

        it('renders a error box when none of the options are checked', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);
            const noButton = screen.getByRole('radio', { name: 'No' });
            const yesButton = screen.getByRole('radio', { name: 'Yes' });

            expect(noButton).not.toBeChecked();
            expect(yesButton).not.toBeChecked();

            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            expect(await screen.findByText('You must select an option')).toBeInTheDocument();
            expect(
                screen.getByText(
                    'Select whether you want to permanently delete these patient files',
                ),
            ).toBeInTheDocument();
        });

        it('change the button to spinner button when deletion is taken place in background', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            mockedAxios.delete.mockReturnValue(waitForSeconds(1));

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            await userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await waitFor(() => {
                expect(screen.getByTestId('delete-submit-spinner-btn')).toBeInTheDocument();
            });
        });

        it('renders patient summary fields', async () => {
            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            const expectedFullName = `${mockPatientDetails.familyName}, ${mockPatientDetails.givenName}`;
            expect(screen.getByText(/Patient name/i)).toBeInTheDocument();
            expect(screen.getByText(expectedFullName)).toBeInTheDocument();

            expect(screen.getByText(/NHS number/i)).toBeInTheDocument();
            const expectedNhsNumber = formatNhsNumber(mockPatientDetails.nhsNumber);
            expect(screen.getByText(expectedNhsNumber)).toBeInTheDocument();

            expect(screen.getByText(/Date of birth/i)).toBeInTheDocument();
            const expectedDob = getFormattedDate(new Date(mockPatientDetails.birthDate));
            expect(screen.getByText(expectedDob)).toBeInTheDocument();
        });
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when error box appears', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE, history);

            const errorResponse = {
                response: {
                    status: 400,
                    message: 'Forbidden',
                },
            };
            mockedAxios.delete.mockRejectedValueOnce(errorResponse);

            await userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
            await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

            await screen.findByText('Sorry, the service is currently unavailable.');

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });
});

describe('Navigation', () => {
    it('navigates to session expire page when API call returns 403', async () => {
        const errorResponse = {
            response: {
                status: 403,
                message: 'Forbidden',
            },
        };
        mockedAxios.delete.mockImplementation(() => Promise.reject(errorResponse));
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

        renderComponent(DOCUMENT_TYPE.ALL, history);

        expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

        await userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
        await userEvent.click(screen.getByRole('button', { name: 'Continue' }));

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
        });
    });
});

const renderComponent = (docType: DOCUMENT_TYPE, history: MemoryHistory) => {
    const props: Omit<Props, 'setStage' | 'setDownloadStage'> = {
        numberOfFiles: mockLgSearchResult.numberOfFiles,
        docType,
        recordType: docType.toString(),
        resetDocState: mockResetDocState,
    };

    return render(
        <ReactRouter.Router navigator={history} location={history.location}>
            <DeleteSubmitStage {...props} />,
        </ReactRouter.Router>,
    );
};
