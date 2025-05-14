import { act, render, screen, waitFor } from '@testing-library/react';
import usePatient from '../../helpers/hooks/usePatient';
import {
    buildLgFile,
    buildPatientDetails,
    buildUploadSession,
} from '../../helpers/test/testBuilders';
import LloydGeorgeUploadPage from './LloydGeorgeUploadPage';
import { routeChildren, routes } from '../../types/generic/routes';
import userEvent from '@testing-library/user-event';
import uploadDocuments, {
    updateDocumentState,
    uploadConfirmation,
    uploadDocumentToS3,
    virusScan,
} from '../../helpers/requests/uploadDocuments';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import { MomentInput } from 'moment/moment';
import * as ReactRouter from 'react-router-dom';
import { History, createMemoryHistory } from 'history';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD } from '../../helpers/utils/uploadAndScanDocumentHelpers';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../helpers/requests/uploadDocuments');
vi.mock('../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../helpers/hooks/usePatient');
vi.mock('../../helpers/utils/waitForSeconds');
vi.mock('react-router-dom', async () => ({
    ...(await vi.importActual('react-router-dom')),
    useNavigate: () => mockNavigate,
}));
Date.now = () => new Date('2020-01-01T00:00:00.000Z').getTime();

const mockedUsePatient = usePatient as Mock;
const mockUploadDocuments = uploadDocuments as Mock;
const mockS3Upload = uploadDocumentToS3 as Mock;
const mockVirusScan = virusScan as Mock;
const mockUploadConfirmation = uploadConfirmation as Mock;
const mockUpdateDocumentState = updateDocumentState as Mock;
const mockNavigate = vi.fn();
const mockPatient = buildPatientDetails();

const lgFile = buildLgFile(1, 1, 'John Doe');

/**
 * Update in other tests
 */
let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe.skip('LloydGeorgeUploadPage', () => {
    beforeEach(() => {
        /**
         * Update in other tests
         */
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });

        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
        mockUploadDocuments.mockImplementation(({ documents }) => buildUploadSession(documents));
    });
    afterEach(() => {
        vi.clearAllMocks();
        vi.useRealTimers();
    });
    describe('Rendering', () => {
        it('renders initial file input stage', () => {
            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
        });

        it('renders file infected stage when virus scan fails', async () => {
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.INFECTED);
            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });

            expect(mockNavigate).toHaveBeenCalledWith(routeChildren.LLOYD_GEORGE_UPLOAD_UPLOADING);
            expect(mockUploadDocuments).toHaveBeenCalled();
            await waitFor(() => {
                expect(mockS3Upload).toHaveBeenCalled();
            });
            expect(mockVirusScan).toHaveBeenCalled();
            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith(
                    routeChildren.LLOYD_GEORGE_UPLOAD_INFECTED,
                );
            });
        });

        it('renders file upload failed stage when file upload fails', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/'],
                initialIndex: 0,
            });
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
            mockUploadConfirmation.mockImplementation(() =>
                Promise.reject({
                    response: {
                        status: 400,
                    },
                }),
            );
            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });

            expect(mockNavigate).toHaveBeenCalledWith(routeChildren.LLOYD_GEORGE_UPLOAD_UPLOADING);
            expect(mockUploadDocuments).toHaveBeenCalled();
            await waitFor(() => {
                expect(mockS3Upload).toHaveBeenCalled();
            });
            expect(mockVirusScan).toHaveBeenCalled();
            await waitFor(() => {
                expect(mockUploadConfirmation).toHaveBeenCalled();
            });
            await waitFor(() => {
                // expect(screen.getByText('Mock file failed stage')).toBeInTheDocument();
                expect(mockNavigate).toHaveBeenCalledWith(routeChildren.LLOYD_GEORGE_UPLOAD_FAILED);
            });
        });

        it.each([1, 2, 3, 4, 5])(
            'renders uploading stage and make call to update state endpoint when submit documents is uploading for more than 2 min',
            async (numberOfTimes: number) => {
                vi.useFakeTimers();

                const expectedTimeTaken =
                    (FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD + 1) * numberOfTimes;
                mockS3Upload.mockImplementationOnce(() => {
                    vi.advanceTimersByTime(expectedTimeTaken + 100);
                    return Promise.resolve();
                });

                mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
                mockUploadConfirmation.mockReturnValue(DOCUMENT_UPLOAD_STATE.SUCCEEDED);
                renderPage(history);
                expect(
                    screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
                ).toBeInTheDocument();
                act(() => {
                    userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
                });
                expect(screen.getByText(lgFile.name)).toBeInTheDocument();
                act(() => {
                    userEvent.click(screen.getByRole('button', { name: 'Upload' }));
                });
                expect(mockUploadDocuments).toHaveBeenCalled();
                await waitFor(() => expect(mockS3Upload).toHaveBeenCalled(), {
                    timeout: expectedTimeTaken + 1000,
                });

                expect(mockUpdateDocumentState).toHaveBeenCalledTimes(numberOfTimes);
                const updateDocumentStateArguments = mockUpdateDocumentState.mock.calls[0][0];
                updateDocumentStateArguments.documents.forEach((doc: UploadDocument) => {
                    expect(doc).toMatchObject({
                        docType: 'LG',
                        ref: expect.stringContaining('uuid_for_file'),
                    });
                });
                expect(mockVirusScan).toHaveBeenCalled();
                expect(mockUploadConfirmation).toHaveBeenCalled();
                expect(mockNavigate).toHaveBeenCalledWith(
                    routeChildren.LLOYD_GEORGE_UPLOAD_COMPLETED,
                );
            },
        );
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            renderPage(history);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigating', () => {
        const postponeByOneTick = () =>
            new Promise((resolve) => {
                setTimeout(resolve, 0);
            });

        it('navigates to uploading stage when submit documents is clicked', async () => {
            mockUploadDocuments.mockImplementationOnce(postponeByOneTick);

            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });
            expect(mockUploadDocuments).toHaveBeenCalled();
            expect(mockNavigate).toHaveBeenCalledWith(routeChildren.LLOYD_GEORGE_UPLOAD_UPLOADING);
        });

        it('navigates to confirmation stage when submit documents is processing', async () => {
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });
            expect(mockUploadDocuments).toHaveBeenCalled();
            await waitFor(() => {
                expect(mockS3Upload).toHaveBeenCalled();
            });
            expect(mockVirusScan).toHaveBeenCalled();
            expect(mockUploadConfirmation).toHaveBeenCalled();
            expect(mockNavigate).toHaveBeenCalledWith(
                routeChildren.LLOYD_GEORGE_UPLOAD_CONFIRMATION,
            );
        });
        it('navigates to complete stage when submit documents is finished', async () => {
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
            mockUploadConfirmation.mockReturnValue(DOCUMENT_UPLOAD_STATE.SUCCEEDED);

            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });
            expect(mockUploadDocuments).toHaveBeenCalled();
            await waitFor(() => {
                expect(mockS3Upload).toHaveBeenCalled();
            });
            await waitFor(() => {
                expect(mockVirusScan).toHaveBeenCalled();
            });
            await waitFor(() => {
                expect(mockUploadConfirmation).toHaveBeenCalled();
            });
            expect(mockNavigate).toHaveBeenCalledWith(routeChildren.LLOYD_GEORGE_UPLOAD_COMPLETED);
        });

        it('navigates to Error page when call to lg record view return 423', async () => {
            const errorResponse = {
                response: {
                    status: 423,
                    data: { message: 'An error occurred', err_code: 'SP_1001' },
                },
            };
            mockUploadDocuments.mockImplementation(() => Promise.reject(errorResponse));

            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });
            expect(mockUploadDocuments).toHaveBeenCalled();

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith(
                    routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
                );
            });
        });
        it('navigates to session expire page when when call to lg record view return 403', async () => {
            const errorResponse = {
                response: {
                    status: 403,
                    data: { message: 'An error occurred', err_code: 'SP_1001' },
                },
            };
            mockUploadDocuments.mockImplementation(() => Promise.reject(errorResponse));

            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });
            expect(mockUploadDocuments).toHaveBeenCalled();

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });
        it('navigates to session expire page when confirmation returns 403', async () => {
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
            mockUploadConfirmation.mockImplementation(() =>
                Promise.reject({
                    response: {
                        status: 403,
                    },
                }),
            );
            renderPage(history);
            expect(
                screen.getByRole('heading', { name: 'Upload a Lloyd George record' }),
            ).toBeInTheDocument();
            act(() => {
                userEvent.upload(screen.getByTestId(`button-input`), [lgFile]);
            });
            expect(screen.getByText(lgFile.name)).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Upload' }));
            });
            expect(mockUploadDocuments).toHaveBeenCalled();
            await waitFor(() => {
                expect(mockS3Upload).toHaveBeenCalled();
            });
            expect(mockVirusScan).toHaveBeenCalled();
            await waitFor(() => {
                expect(mockUploadConfirmation).toHaveBeenCalled();
            });
            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });
    });

    const renderPage = (history: History) => {
        return render(
            <ReactRouter.Router navigator={history} location={history.location}>
                <LloydGeorgeUploadPage />
            </ReactRouter.Router>,
        );
    };
});
