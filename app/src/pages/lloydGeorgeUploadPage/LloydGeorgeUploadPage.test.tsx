import { render, screen, waitFor } from '@testing-library/react';
import usePatient from '../../helpers/hooks/usePatient';
import {
    buildLgFile,
    buildPatientDetails,
    buildUploadSession,
} from '../../helpers/test/testBuilders';
import LloydGeorgeUploadPage from './LloydGeorgeUploadPage';
import userEvent from '@testing-library/user-event';
import uploadDocuments from '../../helpers/requests/uploadDocuments';
import { act } from 'react-dom/test-utils';
import { DOCUMENT_TYPE, DOCUMENT_UPLOAD_STATE } from '../../types/pages/UploadDocumentsPage/types';
jest.mock('../../helpers/requests/uploadDocuments');
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../helpers/hooks/usePatient');
jest.mock('react-router');
const mockedUsePatient = usePatient as jest.Mock;
const mockUploadDocuments = uploadDocuments as jest.Mock;
const mockPatient = buildPatientDetails();
const lgFile = buildLgFile(1, 1, 'John Doe');
const uploadDocument = {
    file: lgFile,
    state: DOCUMENT_UPLOAD_STATE.SELECTED,
    id: '1',
    progress: 50,
    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
    attempts: 0,
};
jest.mock(
    '../../components/blocks/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage',
    () => () => <h1>Mock files are uploading stage</h1>,
);
jest.mock(
    '../../components/blocks/lloydGeorgeUploadCompleteStage/LloydGeorgeUploadCompleteStage',
    () => () => <h1>Mock complete stage</h1>,
);

describe('UploadDocumentsPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
        mockUploadDocuments.mockReturnValue(buildUploadSession([uploadDocument]));
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders initial file input stage', () => {
            render(<LloydGeorgeUploadPage />);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
        });

        it('renders uploading stage when submit documents is clicked', async () => {
            render(<LloydGeorgeUploadPage />);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            await waitFor(() => {
                expect(mockUploadDocuments).toHaveBeenCalled();
            });
            expect(
                screen.getByRole('heading', {
                    name: 'Mock files are uploading stage',
                }),
            ).toBeInTheDocument();
        });
    });
});
