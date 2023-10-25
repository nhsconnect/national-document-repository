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
jest.mock('axios');

const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();
const mockSetStage = jest.fn();
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
    it('renders the page with patient details', async () => {
        const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
        const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));

        renderComponent();

        await waitFor(async () => {
            expect(
                screen.getByText('Are you sure you want to permanently delete files for:')
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
        renderComponent();

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

        renderComponent();

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

const TestApp = (props: Omit<Props, 'setStage' | 'setDownloadStage'>) => {
    return (
        <DeleteDocumentsStage
            {...props}
            setStage={mockSetStage}
            setDownloadStage={mockSetDownloadStage}
        />
    );
};

const renderComponent = () => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };

    const props: Omit<Props, 'setStage' | 'setDownloadStage'> = {
        patientDetails: mockPatientDetails,
        numberOfFiles: mockLgSearchResult.number_of_files,
        docType: DOCUMENT_TYPE.LLOYD_GEORGE,
        passNavigate: mockNavigateCallback,
    };

    render(
        <SessionProvider sessionOverride={auth}>
            <TestApp {...props} />
        </SessionProvider>
    );
};
