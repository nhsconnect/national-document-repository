import { render, screen, waitFor } from '@testing-library/react';
import { buildLgSearchResult, buildPatientDetails } from '../../../helpers/test/testBuilders';
import DeleteDocumentsStage, { Props } from './DeleteDocumentsStage';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { DOCUMENT_TYPE } from '../../../types/pages/UploadDocumentsPage/types';
import axios from 'axios/index';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE, authorisedRoles } from '../../../types/generic/authRole';
import { routes } from '../../../types/generic/routes';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';

jest.mock('../deletionConfirmationStage/DeletionConfirmationStage', () => () => (
    <div>Deletion complete</div>
));
jest.mock('../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../helpers/hooks/useRole');
jest.mock('axios');
const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
const mockedUseRole = useRole as jest.Mock;
const mockedAxios = axios as jest.Mocked<typeof axios>;

const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();

const mockSetStage = jest.fn();
const mockSetIsDeletingDocuments = jest.fn();
const mockSetDownloadStage = jest.fn();

describe('DeleteDocumentsStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Render', () => {
        it.each(authorisedRoles)(
            "renders the page with patient details when user role is '%s'",
            async (role) => {
                const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
                const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));
                mockedUseRole.mockReturnValue(role);

                renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE);

                await waitFor(async () => {
                    expect(
                        screen.getByText('Are you sure you want to permanently delete files for:'),
                    ).toBeInTheDocument();
                });

                expect(screen.getByText(patientName)).toBeInTheDocument();
                expect(screen.getByText(`Date of birth: ${dob}`)).toBeInTheDocument();
                expect(screen.getByText(/NHS number/)).toBeInTheDocument();
                expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
                expect(screen.getByRole('radio', { name: 'No' })).toBeInTheDocument();
                expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();
            },
        );

        it('renders DocumentSearchResults when No is selected and Continue clicked, when user role is GP Admin', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE);

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'No' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
            });
        });

        it('renders DocumentSearchResults when No is selected and Continue clicked, when user role is PCSE', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            renderComponent(DOCUMENT_TYPE.ALL);

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'No' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(mockSetIsDeletingDocuments).toHaveBeenCalledWith(false);
            });
        });

        it('does not render a view DocumentSearchResults when No is selected and Continue clicked, when user role is GP Clinical', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE);

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'No' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(mockSetStage).toHaveBeenCalledTimes(0);
            });
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.PCSE])(
            "renders DeletionConfirmationStage when the Yes is selected and Continue clicked, when user role is '%s'",
            async (role) => {
                mockedAxios.delete.mockReturnValue(
                    Promise.resolve({ status: 200, data: 'Success' }),
                );
                mockedUseRole.mockReturnValue(role);

                renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE);

                expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
                expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

                act(() => {
                    userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
                    userEvent.click(screen.getByRole('button', { name: 'Continue' }));
                });

                await waitFor(() => {
                    expect(screen.getByText('Deletion complete')).toBeInTheDocument();
                });
            },
        );

        it('does not render DeletionConfirmationStage when the Yes is selected, Continue clicked, and user role is GP Clinical', async () => {
            mockedAxios.delete.mockReturnValue(Promise.resolve({ status: 200, data: 'Success' }));
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);

            renderComponent(DOCUMENT_TYPE.LLOYD_GEORGE);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(screen.queryByText('Deletion complete')).not.toBeInTheDocument();
            });
        });

        it('renders a service error when service is down', async () => {
            const errorResponse = {
                response: {
                    status: 500,
                    message: 'Client Error.',
                },
            };
            mockedAxios.delete.mockImplementation(() => Promise.reject(errorResponse));
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
            renderComponent(DOCUMENT_TYPE.ALL);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(
                    screen.getByText('Sorry, the service is currently unavailable.'),
                ).toBeInTheDocument();
            });
        });
    });
});

describe('Navigation', () => {
    it('navigates to home page when API call returns 403', async () => {
        const errorResponse = {
            response: {
                status: 403,
                message: 'Forbidden',
            },
        };
        mockedAxios.delete.mockImplementation(() => Promise.reject(errorResponse));
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

        renderComponent(DOCUMENT_TYPE.ALL);

        expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

        act(() => {
            userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
            userEvent.click(screen.getByRole('button', { name: 'Continue' }));
        });

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
        });
    });
});

const renderComponent = (docType: DOCUMENT_TYPE) => {
    const props: Omit<Props, 'setStage' | 'setIsDeletingDocuments' | 'setDownloadStage'> = {
        patientDetails: mockPatientDetails,
        numberOfFiles: mockLgSearchResult.number_of_files,
        docType,
    };

    render(
        <DeleteDocumentsStage
            {...props}
            setStage={mockSetStage}
            setIsDeletingDocuments={mockSetIsDeletingDocuments}
            setDownloadStage={mockSetDownloadStage}
        />,
    );
};
