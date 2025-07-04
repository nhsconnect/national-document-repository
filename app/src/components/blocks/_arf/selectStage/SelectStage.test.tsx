import { render, screen, waitFor } from '@testing-library/react';
import SelectStage from './SelectStage';
import { buildPatientDetails, buildTextFile } from '../../../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import {
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { PatientDetails } from '../../../../types/generic/patientDetails';
import usePatient from '../../../../helpers/hooks/usePatient';
import { useState } from 'react';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

const mockedUseNavigate = vi.fn();

vi.mock('../../../../helpers/requests/uploadDocuments');
vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../../../helpers/utils/toFileList');
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
    useLocation: () => vi.fn(),
}));
const mockedUsePatient = usePatient as Mock;
const mockPatient = buildPatientDetails();
const documentOne = buildTextFile('one', 100);
const documentTwo = buildTextFile('two', 200);
const documentThree = buildTextFile('three', 100);
const arfDocuments = [documentOne, documentTwo, documentThree];

const setDocumentMock = vi.fn();
setDocumentMock.mockImplementation((document) => {
    document.state = documentUploadStates.SELECTED;
    document.id = '1';
});

const mockStartUpload = vi.fn();

const mockPatientDetails: PatientDetails = buildPatientDetails();
describe('<SelectStage />', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the page', async () => {
            renderApp();

            expect(screen.getByRole('heading', { name: 'Upload documents' })).toBeInTheDocument();
            expect(screen.getByText(mockPatientDetails.nhsNumber)).toBeInTheDocument();
            expect(screen.getByText('Select file(s)')).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
        });

        it.skip('does upload and then remove a file', async () => {
            renderApp();
            await userEvent.upload(screen.getByTestId('ARF-input'), [
                documentOne,
                documentTwo,
                documentThree,
            ]);

            expect(screen.getByText(documentOne.name)).toBeInTheDocument();

            const removeFile = await screen.findByRole('button', {
                name: `Remove ${documentOne.name} from selection`,
            });

            await userEvent.click(removeFile);

            expect(screen.queryByText(documentOne.name)).not.toBeInTheDocument();
            expect(screen.getByText(documentTwo.name)).toBeInTheDocument();
            expect(screen.getByText(documentThree.name)).toBeInTheDocument();
        });

        it('does not upload either forms if selected file is more than 5GB', async () => {
            renderApp();
            const documentBig = buildTextFile('four', 6 * Math.pow(1024, 3));
            const documents = [...arfDocuments, documentBig];

            await userEvent.upload(screen.getByTestId('ARF-input'), documents);

            expect(screen.getByText(documentBig.name)).toBeInTheDocument();

            await userEvent.click(screen.getByText('Upload'));

            expect(
                await screen.findByText('Please ensure that all files are less than 5GB in size'),
            ).toBeInTheDocument();
        });

        it.skip('shows a duplicate file warning if two or more files match name/size for ARF input only', async () => {
            const duplicateFileWarning = 'There are two or more documents with the same name.';
            renderApp();

            await userEvent.upload(screen.getByTestId('ARF-input'), [documentOne, documentOne]);

            await screen.findByText(duplicateFileWarning);

            const removeButtons = await screen.findAllByRole('button', {
                name: `Remove ${documentOne.name} from selection`,
            });

            userEvent.click(removeButtons[1]);

            await waitFor(() => {
                expect(screen.queryByText(duplicateFileWarning)).not.toBeInTheDocument();
            });
        });

        it.skip("does allow the user to add the same file again if they remove for '%s' input", async () => {
            renderApp();
            const selectFilesLabel = screen.getByTestId('ARF-input');

            await userEvent.upload(selectFilesLabel, documentOne);

            const removeFile = await screen.findByRole('button', {
                name: `Remove ${documentOne.name} from selection`,
            });

            await userEvent.click(removeFile);
            await userEvent.upload(selectFilesLabel, documentOne);

            expect(await screen.findByText(documentOne.name)).toBeInTheDocument();
        });

        it('show an alert message when user try to upload with no files selected', async () => {
            renderApp();
            await userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            expect(await screen.findByText('Select a file to upload')).toBeInTheDocument();
        });

        it('renders link to PCSE that opens in a new tab', () => {
            renderApp();
            const pcseLink = screen.getByRole('link', {
                name: 'Primary Care Support England - this link will open in a new tab',
            });
            expect(pcseLink).toHaveAttribute('href', 'https://secure.pcse.england.nhs.uk/');
            expect(pcseLink).toHaveAttribute('target', '_blank');
        });
    });

    describe('Accessibility', () => {
        it('pass accessibility check when some files are selected', async () => {
            renderApp();

            const selectFilesLabel = screen.getByTestId(`ARF-input`);
            await userEvent.upload(selectFilesLabel, documentOne);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('calls startUpload if user selected some files and clicked upload button', async () => {
            renderApp();
            userEvent.upload(screen.getByTestId('ARF-input'), [
                documentOne,
                documentTwo,
                documentThree,
            ]);
            await userEvent.click(screen.getByRole('button', { name: 'Upload' }));

            await waitFor(() => {
                expect(mockStartUpload).toHaveBeenCalledTimes(1);
            });
        });
    });

    const renderApp = () => {
        render(<TestApp />);
    };

    const TestApp = () => {
        const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
        return (
            <SelectStage
                setDocuments={setDocuments}
                documents={documents}
                startUpload={mockStartUpload}
            />
        );
    };
});
