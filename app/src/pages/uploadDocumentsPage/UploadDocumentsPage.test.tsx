import { render, RenderResult, screen, waitFor } from '@testing-library/react';
import UploadDocumentsPage from './UploadDocumentsPage';
import {
    buildConfig,
    buildDocument,
    buildTextFile,
    buildUploadSession,
} from '../../helpers/test/testBuilders';
import useConfig from '../../helpers/hooks/useConfig';
import { routeChildren, routes } from '../../types/generic/routes';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { createMemoryHistory, History } from 'history';
import * as ReactRouter from 'react-router';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../types/pages/UploadDocumentsPage/types';
import uploadDocuments, {
    updateDocumentState,
    uploadConfirmation,
    uploadDocumentToS3,
    virusScan,
} from '../../helpers/requests/uploadDocuments';
import { FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD } from '../../helpers/utils/uploadAndScanDocumentHelpers';

const mockConfigContext = useConfig as jest.Mock;
const mockedUseNavigate = jest.fn();
const mockUploadDocuments = uploadDocuments as jest.Mock;
const mockS3Upload = uploadDocumentToS3 as jest.Mock;
const mockVirusScan = virusScan as jest.Mock;
const mockUpdateDocumentState = updateDocumentState as jest.Mock;
const mockUploadConfirmation = uploadConfirmation as jest.Mock;

jest.mock('react-router', () => ({
    ...jest.requireActual('react-router'),
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('../../helpers/requests/uploadDocuments');
jest.mock('../../helpers/hooks/usePatient');
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../helpers/hooks/useConfig');
jest.mock('../../helpers/utils/waitForSeconds');

const documentOne = buildTextFile('one', 100);
const documentTwo = buildTextFile('two', 200);
const documentThree = buildTextFile('three', 100);
const arfDocuments = [documentOne, documentTwo, documentThree];

let history = createMemoryHistory({
    initialEntries: [routes.ARF_UPLOAD_DOCUMENTS],
    initialIndex: 0,
});

describe('UploadDocumentsPage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: [routes.ARF_UPLOAD_DOCUMENTS],
            initialIndex: 0,
        });

        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockConfigContext.mockReturnValue(
            buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: true }),
        );
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    const setFilesAndClickUpload = (filesToUpload: File[] = []) => {
        if (filesToUpload?.length < 1) {
            filesToUpload = [buildTextFile('arf-test.txt', 100)];
        }

        act(() => {
            userEvent.upload(screen.getByTestId(`ARF-input`), filesToUpload);
            userEvent.click(screen.getByTestId('arf-upload-submit-btn'));
        });
    };

    describe('Rendering', () => {
        it('renders initial file input stage', async () => {
            renderPage(history);

            expect(screen.getByTestId('arf-upload-select-stage-header')).toBeInTheDocument();
            await waitFor(() => {
                expect(mockedUseNavigate).not.toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });

        it('renders a loading screen when upload confirmation is in process', async () => {
            history.push(routeChildren.ARF_UPLOAD_CONFIRMATION);
            renderPage(history);

            expect(screen.getByText('Checking uploads...')).toBeInTheDocument();
        });

        it('pass accessibility checks', async () => {
            renderPage(history);
            const results = await runAxeTest(document.body);

            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        describe('Ensure user authorised', () => {
            it('redirects to unauthorised page if arf workflow feature toggled off', async () => {
                mockConfigContext.mockReturnValue(
                    buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: false }),
                );

                renderPage(history);

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
                });
            });
            it('redirects to unauthorised page if upload lambda feature toggled off', async () => {
                mockConfigContext.mockReturnValue(
                    buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: false }),
                );

                renderPage(history);

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
                });
            });
            it('redirects to unauthorised page if both features toggled off', async () => {
                mockConfigContext.mockReturnValue(
                    buildConfig(
                        {},
                        { uploadArfWorkflowEnabled: false, uploadLambdaEnabled: false },
                    ),
                );

                renderPage(history);

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
                });
            });
        });

        async function uploadFileAndWaitForLoadingScreen(files: File[]) {
            setFilesAndClickUpload(files);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routeChildren.ARF_UPLOAD_UPLOADING);
            });
        }

        describe('Upload journey', () => {
            const successResponse = {
                response: {
                    status: 200,
                },
            };

            beforeEach(() => {
                mockedUseNavigate.mockImplementation((path) => history.push(path));

                const uploadDocs = arfDocuments.map((doc) =>
                    buildDocument(doc, DOCUMENT_UPLOAD_STATE.SELECTED, DOCUMENT_TYPE.ARF),
                );
                const uploadSession = buildUploadSession(uploadDocs);

                mockUploadDocuments.mockResolvedValue(uploadSession);
                mockS3Upload.mockResolvedValue(successResponse);
            });

            it('navigate to uploading page when upload is triggered', async () => {
                renderPage(history);
                setFilesAndClickUpload();

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        routeChildren.ARF_UPLOAD_UPLOADING,
                    );
                });
            });

            it('[happy path] navigate to confirmation page if all files are clean', async () => {
                mockVirusScan.mockResolvedValue(DOCUMENT_UPLOAD_STATE.CLEAN);

                const { rerender } = renderPage(history);

                await uploadFileAndWaitForLoadingScreen(arfDocuments);

                expect(mockUploadDocuments).toHaveBeenCalledTimes(1);
                expect(mockS3Upload).toHaveBeenCalledTimes(arfDocuments.length);
                expect(mockVirusScan).toHaveBeenCalledTimes(arfDocuments.length);

                rerender(<App history={history} />);

                await waitFor(() => {
                    expect(
                        screen.getByRole('heading', { name: 'Your documents are uploading' }),
                    ).toBeInTheDocument();
                });
                expect(mockUploadConfirmation).toHaveBeenCalledTimes(1);

                const confirmedDocuments = mockUploadConfirmation.mock.calls[0][0].documents;
                expect(confirmedDocuments.length).toEqual(arfDocuments.length);

                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routeChildren.ARF_UPLOAD_CONFIRMATION,
                );
                expect(mockedUseNavigate).toHaveBeenCalledWith(routeChildren.ARF_UPLOAD_COMPLETED);
            });

            it('[semi-happy path] navigate to confirmation page if files are a mix of clean and infected', async () => {
                mockVirusScan
                    .mockResolvedValueOnce(DOCUMENT_UPLOAD_STATE.CLEAN)
                    .mockResolvedValueOnce(DOCUMENT_UPLOAD_STATE.INFECTED)
                    .mockResolvedValueOnce(DOCUMENT_UPLOAD_STATE.CLEAN);

                const cleanFilesCount = 2;

                const { rerender } = renderPage(history);

                await uploadFileAndWaitForLoadingScreen(arfDocuments);

                rerender(<App history={history} />);

                await waitFor(() => {
                    expect(mockUploadConfirmation).toHaveBeenCalledTimes(1);
                });

                const documentsForUploadConfirm = mockUploadConfirmation.mock.calls[0][0].documents;
                expect(documentsForUploadConfirm.length).toEqual(cleanFilesCount);

                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routeChildren.ARF_UPLOAD_CONFIRMATION,
                );
                expect(mockedUseNavigate).toHaveBeenCalledWith(routeChildren.ARF_UPLOAD_COMPLETED);
            });

            it('only navigate to confirmation page when every files are scanned', async () => {
                const waitForSeconds = jest.requireActual(
                    '../../helpers/utils/waitForSeconds',
                ).default;

                mockVirusScan
                    .mockImplementationOnce(() => waitForSeconds(99999))
                    .mockResolvedValueOnce(DOCUMENT_UPLOAD_STATE.CLEAN)
                    .mockResolvedValueOnce(DOCUMENT_UPLOAD_STATE.CLEAN);

                const { rerender } = renderPage(history);

                await uploadFileAndWaitForLoadingScreen(arfDocuments);

                rerender(<App history={history} />);

                await waitFor(() => {
                    expect(mockUploadConfirmation).not.toHaveBeenCalled();
                });
                expect(mockedUseNavigate).not.toHaveBeenCalledWith(
                    routeChildren.ARF_UPLOAD_CONFIRMATION,
                );
                expect(mockedUseNavigate).not.toHaveBeenCalledWith(
                    routeChildren.ARF_UPLOAD_COMPLETED,
                );
            });

            describe('setInterval related logics', () => {
                beforeAll(() => {
                    jest.useFakeTimers();
                });
                afterAll(() => {
                    jest.useRealTimers();
                });

                function mockSlowS3Upload(milliseconds: number) {
                    mockS3Upload.mockImplementationOnce(() => {
                        jest.advanceTimersByTime(milliseconds);
                        return Promise.resolve(successResponse);
                    });
                    mockS3Upload.mockResolvedValue(successResponse);
                }
                async function waitForSlowUpload(milliseconds: number) {
                    await waitFor(
                        () => {
                            expect(mockS3Upload).toHaveBeenCalled();
                        },
                        { timeout: milliseconds },
                    );
                }

                it.each([1, 2, 3, 4, 5])(
                    'calls updateDocumentState every 2 minutes during upload',
                    async (numberOfTimes) => {
                        const mockTimeTakenForUpload =
                            FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD * numberOfTimes + 100;

                        mockSlowS3Upload(mockTimeTakenForUpload);

                        renderPage(history);
                        setFilesAndClickUpload(arfDocuments);

                        await waitForSlowUpload(mockTimeTakenForUpload + 1000);

                        expect(mockUpdateDocumentState).toHaveBeenCalledTimes(numberOfTimes);
                        const updateDocumentStateArguments =
                            mockUpdateDocumentState.mock.calls[0][0];
                        expect(updateDocumentStateArguments.uploadingState).toBe(true);
                    },
                );

                it('calls updateDocumentState with correct arguments', async () => {
                    const mockTimeTakenForUpload =
                        FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD + 100;
                    mockSlowS3Upload(mockTimeTakenForUpload);

                    renderPage(history);

                    setFilesAndClickUpload(arfDocuments);
                    await waitForSlowUpload(mockTimeTakenForUpload + 1000);

                    const updateDocumentStateArguments = mockUpdateDocumentState.mock.calls[0][0];

                    expect(updateDocumentStateArguments.uploadingState).toBe(true);
                    expect(updateDocumentStateArguments.documents).toHaveLength(
                        arfDocuments.length,
                    );
                    updateDocumentStateArguments.documents.forEach((doc: UploadDocument) => {
                        expect(doc).toMatchObject({
                            docType: 'ARF',
                            ref: expect.stringContaining('uuid_for_file'),
                        });
                    });
                });
            });

            describe('Error handling', () => {
                const badRequestResponse400 = {
                    response: {
                        status: 400,
                    },
                };
                const unauthorisedResponse403 = {
                    response: {
                        status: 403,
                        message: 'Forbidden',
                    },
                };
                const uploadLockedResponse423 = {
                    response: {
                        status: 423,
                    },
                };
                const badGatewayResponse502 = {
                    response: {
                        status: 502,
                    },
                };

                it('navigates to session expire page when createDocRef call returns 403', async () => {
                    mockUploadDocuments.mockRejectedValue(unauthorisedResponse403);

                    renderPage(history);

                    setFilesAndClickUpload();

                    await waitFor(() => {
                        expect(mockedUseNavigate).toHaveBeenLastCalledWith(routes.SESSION_EXPIRED);
                    });
                });

                it('navigates to error page when createDocRef call returns other error', async () => {
                    mockUploadDocuments.mockRejectedValue(badGatewayResponse502);

                    renderPage(history);

                    setFilesAndClickUpload();

                    await waitFor(() => {
                        expect(mockedUseNavigate).toHaveBeenCalledWith(
                            expect.stringContaining('/server-error?encodedError='),
                        );
                    });
                });

                it('navigates to error page when createDocRef call returns 423', async () => {
                    mockUploadDocuments.mockRejectedValue(uploadLockedResponse423);

                    renderPage(history);

                    setFilesAndClickUpload();

                    await waitFor(() => {
                        expect(mockedUseNavigate).toHaveBeenCalledWith(
                            expect.stringContaining('/server-error?encodedError='),
                        );
                    });
                });

                it('navigates to failed stage if all files could not be uploaded to s3', async () => {
                    mockS3Upload.mockRejectedValue(badRequestResponse400);

                    const { rerender } = renderPage(history);

                    await uploadFileAndWaitForLoadingScreen(arfDocuments);

                    rerender(<App history={history} />);

                    expect(mockUploadConfirmation).not.toHaveBeenCalled();
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routeChildren.ARF_UPLOAD_FAILED);

                    expect(mockUpdateDocumentState).toHaveBeenCalledWith(
                        expect.objectContaining({
                            uploadingState: false,
                        }),
                    );
                });

                it('navigates to failed stage if all files are infected', async () => {
                    mockVirusScan.mockResolvedValue(DOCUMENT_UPLOAD_STATE.INFECTED);

                    const { rerender } = renderPage(history);

                    await uploadFileAndWaitForLoadingScreen(arfDocuments);

                    rerender(<App history={history} />);

                    expect(mockUploadConfirmation).not.toHaveBeenCalled();
                    expect(mockedUseNavigate).toHaveBeenCalledWith(routeChildren.ARF_UPLOAD_FAILED);

                    expect(mockUpdateDocumentState).toHaveBeenCalledWith(
                        expect.objectContaining({
                            uploadingState: false,
                        }),
                    );
                });

                const uploadFilesAndWaitUntilConfirmationCall = async (
                    files: File[],
                    rerender: RenderResult['rerender'],
                ) => {
                    mockVirusScan.mockResolvedValue(DOCUMENT_UPLOAD_STATE.CLEAN);

                    await uploadFileAndWaitForLoadingScreen(files);
                    rerender(<App history={history} />);
                    await waitFor(() => {
                        expect(mockUploadConfirmation).toHaveBeenCalled();
                    });
                };

                it('navigates to session expire page when uploadConfirmation returns 403', async () => {
                    mockUploadConfirmation.mockRejectedValue(unauthorisedResponse403);

                    const { rerender } = renderPage(history);

                    await uploadFilesAndWaitUntilConfirmationCall(arfDocuments, rerender);

                    expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
                });

                it('navigates to session expire page error page when uploadConfirmation returns other error', async () => {
                    mockUploadConfirmation.mockRejectedValue(badRequestResponse400);

                    const { rerender } = renderPage(history);

                    await uploadFilesAndWaitUntilConfirmationCall(arfDocuments, rerender);

                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        expect.stringContaining('/server-error?encodedError='),
                    );
                });
            });
        });
    });
});

type Args = { history: History };

const App = ({ history }: Args) => {
    return (
        <ReactRouter.Router navigator={history} location={history.location}>
            <ReactRouter.Routes>
                <ReactRouter.Route
                    path={routes.ARF_UPLOAD_DOCUMENTS + '/*'}
                    element={<UploadDocumentsPage />}
                ></ReactRouter.Route>
            </ReactRouter.Routes>
        </ReactRouter.Router>
    );
};

const renderPage = (history: History) => {
    return render(<App history={history} />);
};
