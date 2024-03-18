import { render, screen, waitFor } from '@testing-library/react';
import usePatient from '../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import LloydGeorgeUploadPage from './LloydGeorgeUploadPage';
import { Props } from '../../components/blocks/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage';
import userEvent from '@testing-library/user-event';
import uploadDocuments from '../../helpers/requests/uploadDocuments';
jest.mock('../../helpers/requests/uploadDocuments');
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../helpers/hooks/usePatient');
jest.mock('react-router');
const mockedUsePatient = usePatient as jest.Mock;

const mockUploadDocuments = uploadDocuments as jest.Mock;
const mockPatient = buildPatientDetails();

jest.mock(
    '../../components/blocks/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage',
    () => (props: Props) => (
        <>
            <h1>Mock file input stage </h1>

            <button onClick={() => props.submitDocuments()}>Mock Submit Documents</button>
        </>
    ),
);
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
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders initial file input stage', () => {
            render(<LloydGeorgeUploadPage />);
            expect(
                screen.getByRole('heading', { name: 'Mock file input stage' }),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Mock Submit Documents' }),
            ).toBeInTheDocument();
        });

        it('renders uploading stage when submit documents is clicked', async () => {
            render(<LloydGeorgeUploadPage />);
            expect(
                screen.getByRole('heading', { name: 'Mock file input stage' }),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Mock Submit Documents' }),
            ).toBeInTheDocument();
            userEvent.click(screen.getByRole('button', { name: 'Mock Submit Documents' }));
            await waitFor(() => {
                expect(mockUploadDocuments).toHaveBeenCalled();
            });
            expect(
                screen.getByRole('heading', {
                    name: 'Mock files are uploading stage',
                }),
            ).toBeInTheDocument();
        });

        // it('renders upload complete stage when state is set', () => {
        //     render(<LloydGeorgeUploadPage />);
        //     expect(
        //         screen.getByRole('heading', { name: 'Mock complete stage' }),
        //     ).toBeInTheDocument();
        // });
    });
});
