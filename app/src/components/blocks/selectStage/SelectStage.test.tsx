/* eslint-disable testing-library/no-unnecessary-act */
import { render, screen, waitFor } from '@testing-library/react';
import SelectStage from './SelectStage';
import { buildPatientDetails, buildTextFile } from '../../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import { DOCUMENT_UPLOAD_STATE as documentUploadStates } from '../../../types/pages/UploadDocumentsPage/types';
import { act } from 'react-dom/test-utils';
import { PatientDetails } from '../../../types/generic/patientDetails';

jest.mock('../../../helpers/utils/toFileList', () => ({
    __esModule: true,
    default: () => [],
}));

jest.mock('react-router');

describe('<UploadDocumentsPage />', () => {
    describe('upload documents with an NHS number', () => {
        const documentOne = buildTextFile('one', 100);
        const documentTwo = buildTextFile('two', 200);
        const documentThree = buildTextFile('three', 100);

        const setDocumentMock = jest.fn();
        setDocumentMock.mockImplementation((document) => {
            document.state = documentUploadStates.SELECTED;
            document.id = '1';
        });

        const mockPatientDetails: PatientDetails = buildPatientDetails();

        it('renders the page', async () => {
            renderSelectStage(setDocumentMock);

            expect(screen.getByRole('heading', { name: 'Upload documents' })).toBeInTheDocument();
            expect(screen.getByText(mockPatientDetails.nhsNumber)).toBeInTheDocument();
            expect(await screen.findAllByText('Select file(s)')).toHaveLength(2);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();
        });

        it('can upload documents to both LG and ARF forms', async () => {
            renderSelectStage(setDocumentMock);

            expect(screen.getByRole('heading', { name: 'Upload documents' })).toBeInTheDocument();
            expect(screen.getByText(mockPatientDetails.nhsNumber)).toBeInTheDocument();
            expect(await screen.findAllByText('Select file(s)')).toHaveLength(2);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();

            act(() => {
                userEvent.upload(screen.getByTestId('ARF-input'), [
                    documentOne,
                    documentTwo,
                    documentThree,
                ]);
            });

            act(() => {
                userEvent.upload(screen.getByTestId('LG-input'), [
                    documentOne,
                    documentTwo,
                    documentThree,
                ]);
            });

            expect(await screen.findAllByText(documentOne.name)).toHaveLength(2);
            expect(await screen.findAllByText(documentTwo.name)).toHaveLength(2);
            expect(await screen.findAllByText(documentThree.name)).toHaveLength(2);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        });

        it.each([['ARF'], ['LG']])(
            "does upload and then remove a file for '%s' input",
            async (inputType) => {
                renderSelectStage(setDocumentMock);

                act(() => {
                    userEvent.upload(screen.getByTestId(`${inputType}-input`), [
                        documentOne,
                        documentTwo,
                        documentThree,
                    ]);
                });

                expect(screen.getByText(documentOne.name)).toBeInTheDocument();

                const removeFile = await screen.findByRole('button', {
                    name: `Remove ${documentOne.name} from selection`,
                });

                act(() => {
                    userEvent.click(removeFile);
                });

                expect(screen.queryByText(documentOne.name)).not.toBeInTheDocument();
                expect(screen.getByText(documentTwo.name)).toBeInTheDocument();
                expect(screen.getByText(documentThree.name)).toBeInTheDocument();
            },
        );

        it.each([['ARF'], ['LG']])(
            "does not upload either forms if selected file is less than 5GB for '%s' input",
            async (inputType) => {
                renderSelectStage(setDocumentMock);

                const documentBig = buildTextFile('four', 6 * Math.pow(1024, 3));

                act(() => {
                    userEvent.upload(screen.getByTestId(`${inputType}-input`), [
                        documentOne,
                        documentTwo,
                        documentThree,
                        documentBig,
                    ]);
                });

                expect(screen.getByText(documentBig.name)).toBeInTheDocument();

                act(() => {
                    userEvent.click(screen.getByText('Upload'));
                });

                expect(
                    await screen.findByText(
                        'Please ensure that all files are less than 5GB in size',
                    ),
                ).toBeInTheDocument();
            },
        );

        it.each([['ARF'], ['LG']])(
            "shows a duplicate file warning if two or more files match name/size for '%s' input",
            async (inputType) => {
                const duplicateFileWarning = 'There are two or more documents with the same name.';

                renderSelectStage(setDocumentMock);

                act(() => {
                    userEvent.upload(screen.getByTestId(`${inputType}-input`), [
                        documentOne,
                        documentOne,
                    ]);
                });

                await waitFor(() => {
                    expect(screen.getByText(duplicateFileWarning)).toBeInTheDocument();
                });
                act(() => {
                    userEvent.click(
                        screen.getAllByRole('button', {
                            name: `Remove ${documentOne.name} from selection`,
                        })[1],
                    );
                });

                expect(screen.queryByText(duplicateFileWarning)).not.toBeInTheDocument();
            },
        );

        it.each([['ARF'], ['LG']])(
            "does allow the user to add the same file again if they remove for '%s' input",
            async (inputType) => {
                renderSelectStage(setDocumentMock);

                const selectFilesLabel = screen.getByTestId('ARF-input');

                act(() => {
                    userEvent.upload(selectFilesLabel, documentOne);
                });

                const removeFile = await screen.findByRole('button', {
                    name: `Remove ${documentOne.name} from selection`,
                });

                act(() => {
                    userEvent.click(removeFile);
                });
                act(() => {
                    userEvent.upload(selectFilesLabel, documentOne);
                });

                expect(await screen.findByText(documentOne.name)).toBeInTheDocument();
            },
        );

        it('renders link to PCSE that opens in a new tab', () => {
            renderSelectStage(setDocumentMock);

            const pcseLink = screen.getByRole('link', {
                name: 'Primary Care Support England',
            });
            expect(pcseLink).toHaveAttribute('href', 'https://secure.pcse.england.nhs.uk/');
            expect(pcseLink).toHaveAttribute('target', '_blank');
        });
    });
});

const renderSelectStage = (
    setDocumentMock: jest.Mock,
    patientDetails: Partial<PatientDetails> = {},
) => {
    const mockPatient = {
        ...buildPatientDetails(),
        ...patientDetails,
    };
    render(
        <SelectStage
            patientDetails={mockPatient}
            setDocuments={setDocumentMock}
            uploadDocuments={() => {}}
        />,
    );
};
