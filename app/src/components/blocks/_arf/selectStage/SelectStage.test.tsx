import { render, screen, waitFor } from '@testing-library/react';
import SelectStage from './SelectStage';
import {
    buildDocument,
    buildLgFile,
    buildPatientDetails,
    buildTextFile,
    buildUploadSession,
} from '../../../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
    DOCUMENT_UPLOAD_STATE,
    UPLOAD_STAGE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { act } from 'react-dom/test-utils';
import { PatientDetails } from '../../../../types/generic/patientDetails';
import usePatient from '../../../../helpers/hooks/usePatient';
import uploadDocuments, { uploadDocumentToS3 } from '../../../../helpers/requests/uploadDocuments';
import { useState } from 'react';
import { routes } from '../../../../types/generic/routes';

const mockedUseNavigate = jest.fn();

jest.mock('../../../../helpers/requests/uploadDocuments');
const mockSetStage = jest.fn();
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../../../helpers/utils/toFileList', () => ({
    __esModule: true,
    default: () => [],
}));
jest.mock('../../../../helpers/hooks/usePatient');

jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
    useLocation: () => jest.fn(),
}));
const mockedUsePatient = usePatient as jest.Mock;
const mockPatient = buildPatientDetails();
// const mockedAxios = axios as jest.Mocked<typeof axios>;
const documentOne = buildTextFile('one', 100);
const documentTwo = buildTextFile('two', 200);
const documentThree = buildTextFile('three', 100);
// const lgDocumentOne = buildLgFile(1, 2, 'Joe Blogs');
// const lgDocumentTwo = buildLgFile(2, 2, 'Joe Blogs');
const arfDocuments = [documentOne, documentTwo, documentThree];

const mockUploadDocument = uploadDocuments as jest.Mock;
const mockS3Upload = uploadDocumentToS3 as jest.Mock;

const setDocumentMock = jest.fn();
setDocumentMock.mockImplementation((document) => {
    document.state = documentUploadStates.SELECTED;
    document.id = '1';
});

const mockPatientDetails: PatientDetails = buildPatientDetails();
describe('<SelectStage />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the page', async () => {
            renderApp();

            expect(screen.getByRole('heading', { name: 'Upload documents' })).toBeInTheDocument();
            expect(screen.getByText(mockPatientDetails.nhsNumber)).toBeInTheDocument();
            expect(screen.getByText('Select file(s)')).toBeInTheDocument();

            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
        });

        // it.skip('can upload documents to both LG and ARF forms', async () => {
        //     renderApp();
        //     expect(screen.getByRole('heading', { name: 'Upload documents' })).toBeInTheDocument();
        //     expect(screen.getByText(mockPatientDetails.nhsNumber)).toBeInTheDocument();
        //     expect(await screen.findAllByText('Select file(s)')).toHaveLength(2);
        //
        //     expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
        //
        //     act(() => {
        //         userEvent.upload(screen.getByTestId('ARF-input'), [
        //             documentOne,
        //             documentTwo,
        //             documentThree,
        //         ]);
        //     });
        //
        //     act(() => {
        //         userEvent.upload(screen.getByTestId('LG-input'), [lgDocumentOne, lgDocumentTwo]);
        //     });
        //
        //     expect(await screen.findAllByText(documentOne.name)).toHaveLength(1);
        //     expect(await screen.findAllByText(documentTwo.name)).toHaveLength(1);
        //     expect(await screen.findAllByText(documentThree.name)).toHaveLength(1);
        //     expect(await screen.findAllByText(lgDocumentOne.name)).toHaveLength(1);
        //     expect(await screen.findAllByText(lgDocumentTwo.name)).toHaveLength(1);
        //
        //     expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
        // });

        it.each([['ARF']])(
            "does upload and then remove a file for '%s' input",
            async (inputType) => {
                renderApp();
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
            // { name: 'LG', documents: [buildLgFile(1, 2, 'Joe Blogs')] },
        ])(
            "does not upload either forms if selected file is more than 5GB for '%s' input",
            async (inputType) => {
                renderApp();
                const documentBig =
                    inputType.name === 'ARF'
                        ? buildTextFile('four', 6 * Math.pow(1024, 3))
                        : buildLgFile(3, 2, 'Joe Blogs', 6 * Math.pow(1024, 3));
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

        // it.skip('does not upload LG form if selected file is not PDF', async () => {
        //     renderApp();
        //     const lgFileWithBadType = new File(
        //         ['test'],
        //         `1of2000_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf`,
        //         {
        //             type: 'text/plain',
        //         },
        //     );
        //
        //     act(() => {
        //         userEvent.upload(screen.getByTestId(`LG-input`), lgFileWithBadType);
        //     });
        //
        //     expect(screen.getByText(lgFileWithBadType.name)).toBeInTheDocument();
        //
        //     act(() => {
        //         userEvent.click(screen.getByText('Upload'));
        //     });
        //
        //     expect(
        //         await screen.findByText(
        //             'One or more of the files do not match the required file type. Please check the file(s) and try again',
        //         ),
        //     ).toBeInTheDocument();
        // });

        // it.skip('does not upload LG form if total number of file does not match file name', async () => {
        //     renderApp();
        //     const lgExtraFile = buildLgFile(3, 3, 'Joe Blogs');
        //
        //     act(() => {
        //         userEvent.upload(screen.getByTestId(`LG-input`), lgExtraFile);
        //     });
        //
        //     expect(screen.getByText(lgExtraFile.name)).toBeInTheDocument();
        //
        //     act(() => {
        //         userEvent.click(screen.getByText('Upload'));
        //     });
        //
        //     expect(
        //         await screen.findByText(
        //             'One or more of the files do not match the required filename format. Please check the file(s) and try again',
        //         ),
        //     ).toBeInTheDocument();
        // });

        // it.skip('does not upload LG form if selected file does not match naming conventions', async () => {
        //     renderApp();
        //     const pdfFileWithBadName = new File(['test'], `test_not_up_to_naming_conventions.pdf`, {
        //         type: 'application/pdf',
        //     });
        //     act(() => {
        //         userEvent.upload(screen.getByTestId(`LG-input`), pdfFileWithBadName);
        //     });
        //
        //     expect(screen.getByText(pdfFileWithBadName.name)).toBeInTheDocument();
        //
        //     act(() => {
        //         userEvent.click(screen.getByText('Upload'));
        //     });
        //
        //     expect(
        //         await screen.findByText(
        //             'One or more of the files do not match the required filename format. Please check the file(s) and try again',
        //         ),
        //     ).toBeInTheDocument();
        // });

        // it.skip('does not upload LG form if selected file number is bigger than number of total files', async () => {
        //     renderApp();
        //     const pdfFileWithBadNumber = buildLgFile(2, 1, 'Joe Blogs');
        //     act(() => {
        //         userEvent.upload(screen.getByTestId(`LG-input`), pdfFileWithBadNumber);
        //     });
        //
        //     expect(screen.getByText(pdfFileWithBadNumber.name)).toBeInTheDocument();
        //
        //     act(() => {
        //         userEvent.click(screen.getByText('Upload'));
        //     });
        //
        //     expect(
        //         await screen.findByText(
        //             'One or more of the files do not match the required filename format. Please check the file(s) and try again',
        //         ),
        //     ).toBeInTheDocument();
        // });

        // it.skip('does not upload LG form if files do not match each other', async () => {
        //     renderApp();
        //     const joeBloggsFile = new File(
        //         ['test'],
        //         `1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf`,
        //         {
        //             type: 'application/pdf',
        //         },
        //     );
        //     const johnSmithFile = new File(
        //         ['test'],
        //         `2of2_Lloyd_George_Record_[John Smith]_[9876543210]_[25-12-2019].pdf`,
        //         {
        //             type: 'application/pdf',
        //         },
        //     );
        //     act(() => {
        //         userEvent.upload(screen.getByTestId(`LG-input`), [joeBloggsFile, johnSmithFile]);
        //     });
        //
        //     expect(screen.getByText(joeBloggsFile.name)).toBeInTheDocument();
        //     expect(screen.getByText(johnSmithFile.name)).toBeInTheDocument();
        //
        //     act(() => {
        //         userEvent.click(screen.getByText('Upload'));
        //     });
        //
        //     expect(
        //         await screen.findByText(
        //             'One or more of the files do not match the required filename format. Please check the file(s) and try again',
        //         ),
        //     ).toBeInTheDocument();
        // });

        // it.skip('does not upload LG form if two or more files match name/size', async () => {
        //     const duplicateFileWarning = 'There are two or more documents with the same name.';
        //     renderApp();
        //     act(() => {
        //         userEvent.upload(screen.getByTestId(`LG-input`), [lgDocumentTwo, lgDocumentTwo]);
        //     });
        //
        //     expect(screen.getAllByText(lgDocumentTwo.name)).toHaveLength(2);
        //
        //     act(() => {
        //         userEvent.click(screen.getByText('Upload'));
        //     });
        //
        //     expect(
        //         await screen.findByText(
        //             'There are documents chosen that have the same name, a record with duplicate file names can not be uploaded because it does not match the required file format. Please check the files(s) and try again.',
        //         ),
        //     ).toBeInTheDocument();
        //     expect(screen.queryByText(duplicateFileWarning)).not.toBeInTheDocument();
        // });

        it.each([['ARF']])(
            'shows a duplicate file warning if two or more files match name/size for ARF input only',
            async (inputType) => {
                const duplicateFileWarning = 'There are two or more documents with the same name.';
                renderApp();
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

        it.each([['ARF']])(
            "does allow the user to add the same file again if they remove for '%s' input",
            async (inputType) => {
                renderApp();
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

        it('show an alert message when user try to upload with no files selected', async () => {
            renderApp();
            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });
            expect(await screen.findByText('Select a file to upload')).toBeInTheDocument();
        });

        it('renders link to PCSE that opens in a new tab', () => {
            renderApp();
            const pcseLink = screen.getByRole('link', {
                name: '(Primary Care Support England - this link will open in a new tab)',
            });
            expect(pcseLink).toHaveAttribute('href', 'https://secure.pcse.england.nhs.uk/');
            expect(pcseLink).toHaveAttribute('target', '_blank');
        });
    });

    describe('Navigation', () => {
        it('sets stage to uploading and complete when upload files is triggered', async () => {
            const response = {
                response: {
                    status: 200,
                },
            };
            const uploadDocs = [documentOne, documentTwo, documentThree].map((doc) =>
                buildDocument(doc, DOCUMENT_UPLOAD_STATE.SELECTED, DOCUMENT_TYPE.ARF),
            );
            const uploadSession = buildUploadSession(uploadDocs);
            mockUploadDocument.mockResolvedValueOnce(uploadSession);
            mockS3Upload.mockResolvedValue(response);

            renderApp();

            act(() => {
                userEvent.upload(screen.getByTestId('ARF-input'), [
                    documentOne,
                    documentTwo,
                    documentThree,
                ]);
            });

            // act(() => {
            //     userEvent.upload(screen.getByTestId('LG-input'), [lgDocumentOne, lgDocumentTwo]);
            // });

            expect(await screen.findAllByText(documentOne.name)).toHaveLength(1);
            expect(await screen.findAllByText(documentTwo.name)).toHaveLength(1);
            expect(await screen.findAllByText(documentThree.name)).toHaveLength(1);
            // expect(await screen.findAllByText(lgDocumentOne.name)).toHaveLength(1);
            // expect(await screen.findAllByText(lgDocumentTwo.name)).toHaveLength(1);

            expect(screen.getByRole('button', { name: 'Upload' })).toBeEnabled();
            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });
            await waitFor(() => {
                expect(mockSetStage).toHaveBeenCalledWith(UPLOAD_STAGE.Uploading);
            });
            await waitFor(() => {
                expect(mockSetStage).toHaveBeenCalledWith(UPLOAD_STAGE.Complete);
            });
        });

        it('navigates to session expire page when API returns 403', async () => {
            const errorResponse = {
                response: {
                    status: 403,
                    message: 'Forbidden',
                },
            };
            mockUploadDocument.mockRejectedValue(errorResponse);

            renderApp();
            act(() => {
                userEvent.upload(screen.getByTestId('ARF-input'), [documentOne]);
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });

        it('navigates to error page when API returns other error', async () => {
            const errorResponse = {
                response: {
                    status: 502,
                },
            };
            mockUploadDocument.mockRejectedValue(errorResponse);

            renderApp();
            act(() => {
                userEvent.upload(screen.getByTestId('ARF-input'), [documentOne]);
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    expect.stringContaining('/server-error?encodedError='),
                );
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
                setStage={mockSetStage}
                documents={documents}
            />
        );
    };
});
