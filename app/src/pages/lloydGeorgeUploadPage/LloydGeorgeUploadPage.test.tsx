import { render, screen, waitFor } from '@testing-library/react';
import usePatient from '../../helpers/hooks/usePatient';
import {
    buildLgFile,
    buildPatientDetails,
    buildUploadSession,
} from '../../helpers/test/testBuilders';
import LloydGeorgeUploadPage from './LloydGeorgeUploadPage';
import { routes } from '../../types/generic/routes';
import userEvent from '@testing-library/user-event';
import uploadDocuments, {
    updateDocumentState,
    uploadConfirmation,
    uploadDocumentToS3,
    virusScanResult,
} from '../../helpers/requests/uploadDocuments';
import { act } from 'react-dom/test-utils';
import { DOCUMENT_TYPE, DOCUMENT_UPLOAD_STATE } from '../../types/pages/UploadDocumentsPage/types';
import { Props } from '../../components/blocks/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage';
import { MomentInput } from 'moment/moment';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

jest.mock('../../helpers/requests/uploadDocuments');
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../helpers/hooks/usePatient');
jest.mock('react-router');
jest.mock('moment', () => {
    return (arg: MomentInput) => {
        if (!arg) {
            arg = '2020-01-01T00:00:00.000Z';
        }
        return jest.requireActual('moment')(arg);
    };
});

const mockedUsePatient = usePatient as jest.Mock;
const mockUploadDocuments = uploadDocuments as jest.Mock;
const mockS3Upload = uploadDocumentToS3 as jest.Mock;
const mockVirusScan = virusScanResult as jest.Mock;
const mockUploadConfirmation = uploadConfirmation as jest.Mock;
const mockUpdateDocumentState = updateDocumentState as jest.Mock;
const mockNavigate = jest.fn();
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
    () =>
        ({ documents }: Props) => (
            <>
                <h1>Mock files are uploading stage</h1>
                {documents.map((d) => (
                    <output key={d.id}>{d.file.name}</output>
                ))}
            </>
        ),
);

jest.mock(
    '../../components/blocks/lloydGeorgeUploadCompleteStage/LloydGeorgeUploadCompleteStage',
    () => () => <h1>Mock complete stage</h1>,
);
jest.mock(
    '../../components/blocks/lloydGeorgeUploadInfectedStage/LloydGeorgeUploadInfectedStage',
    () => () => <h1>Mock virus infected stage</h1>,
);
jest.mock(
    '../../components/blocks/lloydGeorgeUploadFailedStage/LloydGeorgeUploadFailedStage',
    () => () => <h1>Mock file failed stage</h1>,
);
jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));

describe('LloydGeorgeUploadPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
        mockUploadDocuments.mockReturnValue(buildUploadSession([uploadDocument]));
    });
    afterEach(() => {
        jest.clearAllMocks();
        jest.useRealTimers();
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
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
            mockUploadConfirmation.mockReturnValue(DOCUMENT_UPLOAD_STATE.SUCCEEDED);
            render(<LloydGeorgeUploadPage />);
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

            expect(
                screen.getByRole('heading', {
                    name: 'Mock files are uploading stage',
                }),
            ).toBeInTheDocument();
            expect(screen.getByText(uploadDocument.file.name)).toBeInTheDocument();

            await waitFor(() => {
                expect(mockS3Upload).toHaveBeenCalled();
            });
            expect(mockVirusScan).toHaveBeenCalled();
            expect(mockUpdateDocumentState).not.toHaveBeenCalled();
            await waitFor(() => {
                expect(mockUploadConfirmation).toHaveBeenCalled();
            });
            await waitFor(() => {
                expect(screen.getByText('Mock complete stage')).toBeInTheDocument();
            });
        });
        it('renders confirmation stage when submit documents is processing', async () => {
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
            render(<LloydGeorgeUploadPage />);
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
            expect(screen.getByRole('status')).toBeInTheDocument();
            expect(screen.getByText('Checking uploads...')).toBeInTheDocument();
        });

        it('renders complete stage when submit documents is finished', async () => {
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
            mockUploadConfirmation.mockReturnValue(DOCUMENT_UPLOAD_STATE.SUCCEEDED);

            render(<LloydGeorgeUploadPage />);
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
                expect(screen.getByText('Mock complete stage')).toBeInTheDocument();
            });
        });

        it('renders file infected stage when virus scan fails', async () => {
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.INFECTED);
            render(<LloydGeorgeUploadPage />);
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
            expect(screen.getByText('Mock virus infected stage')).toBeInTheDocument();
        });

        it('renders file upload failed stage when file upload fails', async () => {
            mockS3Upload.mockReturnValue(Promise.resolve());
            mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
            mockUploadConfirmation.mockImplementation(() =>
                Promise.reject({
                    response: {
                        status: 400,
                    },
                }),
            );
            render(<LloydGeorgeUploadPage />);
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
                expect(screen.getByText('Mock file failed stage')).toBeInTheDocument();
            });
        });

        it.each([1, 2, 3, 4, 5])(
            'renders uploading stage and make call to update state endpoint when submit documents is uploading for more than 2 min',
            async (numberOfTimes: number) => {
                jest.useFakeTimers();

                const expectedTimeTaken = 120001 * numberOfTimes;
                mockS3Upload.mockImplementationOnce(() => {
                    jest.advanceTimersByTime(expectedTimeTaken + 100);
                    return Promise.resolve();
                });

                mockVirusScan.mockReturnValue(DOCUMENT_UPLOAD_STATE.CLEAN);
                mockUploadConfirmation.mockReturnValue(DOCUMENT_UPLOAD_STATE.SUCCEEDED);
                render(<LloydGeorgeUploadPage />);
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
                expect(mockVirusScan).toHaveBeenCalled();
                expect(mockUploadConfirmation).toHaveBeenCalled();
                expect(screen.getByText('Mock complete stage')).toBeInTheDocument();
            },
        );
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            render(<LloydGeorgeUploadPage />);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigating', () => {
        it('navigates to Error page when call to lg record view return 423', async () => {
            const errorResponse = {
                response: {
                    status: 423,
                    data: { message: 'An error occurred', err_code: 'SP_1001' },
                },
            };
            mockUploadDocuments.mockImplementation(() => Promise.reject(errorResponse));

            render(<LloydGeorgeUploadPage />);
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

            render(<LloydGeorgeUploadPage />);
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
            render(<LloydGeorgeUploadPage />);
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
});
