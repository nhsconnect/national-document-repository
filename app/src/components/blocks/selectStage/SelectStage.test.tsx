/* eslint-disable testing-library/no-unnecessary-act */
import { render, screen, waitFor } from '@testing-library/react';
import SelectStage from './SelectStage';
import {
    buildPatientDetails,
    buildTextFile,
    buildLgFile,
} from '../../../helpers/test/testBuilders';
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
        const lgDocumentOne = buildLgFile(1, 2);
        const lgDocumentTwo = buildLgFile(2, 2);
        const arfDocuments = [documentOne, documentTwo, documentThree];

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
                userEvent.upload(screen.getByTestId('LG-input'), [lgDocumentOne, lgDocumentTwo]);
            });

            expect(await screen.findAllByText(documentOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(documentTwo.name)).toHaveLength(1);
            expect(await screen.findAllByText(documentThree.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(lgDocumentTwo.name)).toHaveLength(1);

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

        it.each([
            { name: 'ARF', documents: arfDocuments },
            { name: 'LG', documents: [buildLgFile(1, 2)] },
        ])(
            "does not upload either forms if selected file is more than 5GB for '%s' input",
            async (inputType) => {
                renderSelectStage(setDocumentMock);

                const documentBig =
                    inputType.name === 'ARF'
                        ? buildTextFile('four', 6 * Math.pow(1024, 3))
                        : buildLgFile(3, 2, 6 * Math.pow(1024, 3));
                inputType.documents.push(documentBig);

                act(() => {
                    userEvent.upload(
                        screen.getByTestId(`${inputType.name}-input`),
                        inputType.documents,
                    );
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

        it('does not upload LG form if selected file is not PDF', async () => {
            renderSelectStage(setDocumentMock);
            const lgFileWithBadType = new File(
                ['test'],
                `1of2000_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf`,
                {
                    type: 'text/plain',
                },
            );

            act(() => {
                userEvent.upload(screen.getByTestId(`LG-input`), lgFileWithBadType);
            });

            expect(
                screen.getByText(
                    '1of2000_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf',
                ),
            ).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'One or more of the files do not match the required file type. Please check the file(s) and try again',
                ),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if total number of file does not match file name', async () => {
            renderSelectStage(setDocumentMock);
            const lgExtraFile = buildLgFile(3, 3);

            act(() => {
                userEvent.upload(screen.getByTestId(`LG-input`), lgExtraFile);
            });

            expect(
                screen.getByText(
                    '3of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf',
                ),
            ).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'One or more of the files do not match the required filename format. Please check the file(s) and try again',
                ),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if selected file does not match naming conventions', async () => {
            renderSelectStage(setDocumentMock);
            const pdfFileWithBadName = new File(['test'], `test_not_up_to_naming_conventions.pdf`, {
                type: 'application/pdf',
            });
            act(() => {
                userEvent.upload(screen.getByTestId(`LG-input`), pdfFileWithBadName);
            });

            expect(screen.getByText('test_not_up_to_naming_conventions.pdf')).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'One or more of the files do not match the required filename format. Please check the file(s) and try again',
                ),
            ).toBeInTheDocument();
        });

        it('does not upload LG form if two or more files match name/size', async () => {
            renderSelectStage(setDocumentMock);
            const duplicateFileWarning = 'There are two or more documents with the same name.';
            act(() => {
                userEvent.upload(screen.getByTestId(`LG-input`), [lgDocumentTwo, lgDocumentTwo]);
            });

            expect(
                screen.getAllByText(
                    '2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf',
                ),
            ).toHaveLength(2);

            act(() => {
                userEvent.click(screen.getByText('Upload'));
            });

            expect(
                await screen.findByText(
                    'There are documents chosen that have the same name, a record with duplicate file names can not be uploaded because it does not match the required file format. Please check the files(s) and try again.',
                ),
            ).toBeInTheDocument();
            expect(screen.queryByText(duplicateFileWarning)).not.toBeInTheDocument();
        });

        it.each([['ARF']])(
            'shows a duplicate file warning if two or more files match name/size for ARF input only',
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

                const selectFilesLabel = screen.getByTestId(`${inputType}-input`);

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
