import { render, screen, waitFor } from '@testing-library/react';
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
import { DOCUMENT_TYPE, DOCUMENT_UPLOAD_STATE } from '../../types/pages/UploadDocumentsPage/types';
import uploadDocuments, {
    uploadConfirmation,
    uploadDocumentToS3,
    virusScan,
} from '../../helpers/requests/uploadDocuments';

const mockConfigContext = useConfig as jest.Mock;
const mockedUseNavigate = jest.fn();
const mockUploadDocument = uploadDocuments as jest.Mock;
const mockS3Upload = uploadDocumentToS3 as jest.Mock;
const mockVirusScan = virusScan as jest.Mock;
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

        describe('Upload journey', () => {
            beforeEach(() => {
                mockedUseNavigate.mockImplementation((path) => history.push(path));
                const successResponse = {
                    response: {
                        status: 200,
                    },
                };
                const uploadDocs = arfDocuments.map((doc) =>
                    buildDocument(doc, DOCUMENT_UPLOAD_STATE.SELECTED, DOCUMENT_TYPE.ARF),
                );
                const uploadSession = buildUploadSession(uploadDocs);

                mockUploadDocument.mockResolvedValueOnce(uploadSession);
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

                setFilesAndClickUpload(arfDocuments);

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        routeChildren.ARF_UPLOAD_UPLOADING,
                    );
                });

                expect(mockUploadDocument).toHaveBeenCalledTimes(1);
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

                setFilesAndClickUpload(arfDocuments);

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        routeChildren.ARF_UPLOAD_UPLOADING,
                    );
                });

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

            it('[unhappy path] navigate to failed page if all files are infected', async () => {
                mockVirusScan.mockResolvedValue(DOCUMENT_UPLOAD_STATE.INFECTED);

                const { rerender } = renderPage(history);

                setFilesAndClickUpload(arfDocuments);

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        routeChildren.ARF_UPLOAD_UPLOADING,
                    );
                });
                rerender(<App history={history} />);

                expect(mockUploadConfirmation).not.toHaveBeenCalled();
                expect(mockedUseNavigate).toHaveBeenCalledWith(routeChildren.ARF_UPLOAD_FAILED);
            });
        });

        describe('Error handling', () => {
            it('navigates to session expire page when API returns 403', async () => {
                const errorResponse = {
                    response: {
                        status: 403,
                        message: 'Forbidden',
                    },
                };
                mockUploadDocument.mockRejectedValue(errorResponse);

                renderPage(history);

                setFilesAndClickUpload();

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

                renderPage(history);

                setFilesAndClickUpload();

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        expect.stringContaining('/server-error?encodedError='),
                    );
                });
            });

            it('navigates to error page when API returns 423', async () => {
                const errorResponse = {
                    response: {
                        status: 423,
                    },
                };
                mockUploadDocument.mockRejectedValue(errorResponse);

                renderPage(history);

                setFilesAndClickUpload();

                await waitFor(() => {
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
