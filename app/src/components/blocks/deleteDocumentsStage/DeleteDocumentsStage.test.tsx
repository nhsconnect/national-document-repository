import { render, screen, waitFor } from '@testing-library/react';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import {
    buildLgSearchResult,
    buildPatientDetails,
    buildUserAuth,
} from '../../../helpers/test/testBuilders';
import DeleteDocumentsStage, { Props } from './DeleteDocumentsStage';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { DOCUMENT_TYPE } from '../../../types/pages/UploadDocumentsPage/types';
import axios from 'axios/index';
import { USER_ROLE } from '../../../types/generic/roles';
import { BrowserRouter } from 'react-router-dom';
jest.mock('axios');

const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();
const mockSetStage = jest.fn();
const mockSetIsDeletingDocuments = jest.fn();
const mockSetDownloadStage = jest.fn();
const mockNavigateCallback = jest.fn();
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('DeleteAllDocumentsStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('GP USER', () => {
        it('renders the page with patient details', async () => {
            const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
            const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));

            renderComponent(USER_ROLE.GP, DOCUMENT_TYPE.LLOYD_GEORGE);

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
        });

        it('renders LgRecordStage when the No radio button is selected and Continue button clicked', async () => {
            renderComponent(USER_ROLE.GP, DOCUMENT_TYPE.LLOYD_GEORGE);

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'No' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
            });
        });

        it('renders DeletionConfirmationStage when the Yes radio button is selected and Continue button clicked', async () => {
            mockedAxios.delete.mockReturnValue(Promise.resolve({ status: 200, data: 'Success' }));

            renderComponent(USER_ROLE.GP, DOCUMENT_TYPE.LLOYD_GEORGE);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });
        });
    });

    describe('PCSE USER', () => {
        it('renders the page with patient details', async () => {
            const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
            const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));

            renderComponent(USER_ROLE.PCSE, DOCUMENT_TYPE.ALL);

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
        });

        it('renders Document search results when the No radio button is selected and Continue button clicked', async () => {
            renderComponent(USER_ROLE.PCSE, DOCUMENT_TYPE.ALL);

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'No' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(mockSetIsDeletingDocuments).toHaveBeenCalledWith(false);
            });
        });

        it('renders DeletionConfirmationStage when the Yes radio button is selected and Continue button clicked', async () => {
            mockedAxios.delete.mockReturnValue(Promise.resolve({ status: 200, data: 'Success' }));

            renderComponent(USER_ROLE.PCSE, DOCUMENT_TYPE.ALL);

            expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('radio', { name: 'Yes' }));
                userEvent.click(screen.getByRole('button', { name: 'Continue' }));
            });

            await waitFor(() => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });
        });
    });
});

const TestApp = (
    props: Omit<Props, 'setStage' | 'setIsDeletingDocuments' | 'setDownloadStage'>,
) => {
    return (
        <DeleteDocumentsStage
            {...props}
            setStage={mockSetStage}
            setIsDeletingDocuments={mockSetIsDeletingDocuments}
            setDownloadStage={mockSetDownloadStage}
        />
    );
};

const renderComponent = (userType: USER_ROLE, docType: DOCUMENT_TYPE) => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };

    const props: Omit<Props, 'setStage' | 'setIsDeletingDocuments' | 'setDownloadStage'> = {
        patientDetails: mockPatientDetails,
        numberOfFiles: mockLgSearchResult.number_of_files,
        userType,
        docType,
        passNavigate: mockNavigateCallback,
    };

    render(
        <SessionProvider sessionOverride={auth}>
            <BrowserRouter>
                <TestApp {...props} />
            </BrowserRouter>
        </SessionProvider>,
    );
};
