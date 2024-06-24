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
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('UploadDocumentsPage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
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

    const setFileAndClickUpload = () => {
        const arfFile = buildTextFile('arf-test.txt', 100);

        act(() => {
            userEvent.upload(screen.getByTestId(`ARF-input`), [arfFile]);
            userEvent.click(screen.getByTestId('arf-upload-submit-btn'));
        });
    };

    const changeStage = (route: routeChildren) => {
        const childRoute = '/' + route.split('/').at(-1);
        history.push(childRoute);
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
            changeStage(routeChildren.ARF_UPLOAD_CONFIRMATION);

            renderPage(history);

            await waitFor(() => {
                expect(screen.getByText('Checking uploads...')).toBeInTheDocument();
            });
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
            it('navigate to uploading page when upload is triggered', async () => {
                renderPage(history);
                setFileAndClickUpload();

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        routeChildren.ARF_UPLOAD_UPLOADING,
                    );
                });
            });

            it('calls the backend APIs when files are being uploaded', async () => {
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
                mockVirusScan.mockResolvedValue(successResponse);

                renderPage(history);

                act(() => {
                    userEvent.upload(screen.getByTestId('ARF-input'), arfDocuments);
                    userEvent.click(screen.getByRole('button', { name: 'Upload' }));
                });

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        routeChildren.ARF_UPLOAD_UPLOADING,
                    );
                });

                expect(mockUploadDocument).toHaveBeenCalledTimes(1);
                expect(mockS3Upload).toHaveBeenCalledTimes(arfDocuments.length);
                expect(mockVirusScan).toHaveBeenCalledTimes(arfDocuments.length);
            });

            it('calls uploadConfirmation when all files are scanned', async () => {});

            // it('calls uploadConfirmation when all files are scanned', async () => {
            //     // eslint-disable-next-line testing-library/render-result-naming-convention
            //     const rerenderPage = renderPage(history);
            //
            //     changeStage(routeChildren.ARF_UPLOAD_FAILED);
            //
            //     rerenderPage(history);
            //
            //     await waitFor(() => {
            //         expect(screen.getByText('Failed to upload documents')).toBeInTheDocument();
            //     });
            // });
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

                setFileAndClickUpload();

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

                setFileAndClickUpload();

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

                setFileAndClickUpload();

                await waitFor(() => {
                    expect(mockedUseNavigate).toHaveBeenCalledWith(
                        expect.stringContaining('/server-error?encodedError='),
                    );
                });
            });
        });
    });
});

const renderPage = (history: History) => {
    const { rerender } = render(
        <ReactRouter.Router navigator={history} location={history.location}>
            <UploadDocumentsPage />
        </ReactRouter.Router>,
    );

    return (updatedHistory: History) =>
        rerender(
            <ReactRouter.Router navigator={updatedHistory} location={updatedHistory.location}>
                <UploadDocumentsPage />
            </ReactRouter.Router>,
        );
};
