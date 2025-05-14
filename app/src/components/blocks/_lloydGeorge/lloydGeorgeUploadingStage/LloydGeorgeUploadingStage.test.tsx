import { act, cleanup, render, screen } from '@testing-library/react';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import {
    buildPatientDetails,
    buildTextFile,
    buildUploadSession,
} from '../../../../helpers/test/testBuilders';
import LloydGeorgeUploadStage from './LloydGeorgeUploadingStage';
import usePatient from '../../../../helpers/hooks/usePatient';
import userEvent from '@testing-library/user-event';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('../../../../helpers/requests/uploadDocuments');

const mockUploadAndScan = vi.fn();
const mockedUsePatient = usePatient as Mock;
const mockPatient = buildPatientDetails();
const nhsNumber = mockPatient.nhsNumber;

describe.skip('<LloydGeorgeUploadingStage />', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    const getProgressBarValue = (document: UploadDocument) => {
        const progressBar: HTMLProgressElement = screen.getByRole('progressbar', {
            name: `Uploading ${document.file.name}`,
        });
        return progressBar.value;
    };
    const getProgressText = (document: UploadDocument) => {
        return screen.getByRole('status', {
            name: `${document.file.name} upload status`,
        }).textContent;
    };

    const triggerUploadStateChange = (
        document: UploadDocument,
        state: DOCUMENT_UPLOAD_STATE,
        { progress, attempts }: { progress: number; attempts?: number },
    ) => {
        act(() => {
            document.state = state;
            document.progress = progress;
            document.attempts = attempts ?? document.attempts;
        });
    };

    describe('Rendering', () => {
        it('renders document with state and progress', async () => {
            const uploadDocument = {
                file: buildTextFile('one', 100),
                state: DOCUMENT_UPLOAD_STATE.UPLOADING,
                id: '1',
                progress: 50,
                docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                attempts: 0,
            };

            const uploadSession = buildUploadSession([uploadDocument]);
            render(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );

            triggerUploadStateChange(uploadDocument, DOCUMENT_UPLOAD_STATE.UPLOADING, {
                progress: 0,
            });

            expect(screen.queryByTestId('upload-document-form')).not.toBeInTheDocument();
            expect(
                screen.getByText(
                    'Do not close or navigate away from this browser until upload is complete. Each file will be uploaded and combined into one record.',
                ),
            ).toBeInTheDocument();
            expect(screen.getByText('50% uploaded...')).toBeInTheDocument();
        });

        it('renders a progress bar that reflects changes in document upload progress', async () => {
            const uploadDocument = {
                file: buildTextFile('one', 100),
                state: DOCUMENT_UPLOAD_STATE.SELECTED,
                id: '1',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };
            const uploadSession = buildUploadSession([uploadDocument]);

            const { rerender } = render(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );

            triggerUploadStateChange(uploadDocument, DOCUMENT_UPLOAD_STATE.UPLOADING, {
                progress: 10,
            });
            rerender(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );
            expect(getProgressBarValue(uploadDocument)).toEqual(10);
            expect(getProgressText(uploadDocument)).toContain('10% uploaded...');

            triggerUploadStateChange(uploadDocument, DOCUMENT_UPLOAD_STATE.UPLOADING, {
                progress: 70,
            });
            rerender(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );
            expect(getProgressBarValue(uploadDocument)).toEqual(70);
            expect(getProgressText(uploadDocument)).toContain('70% uploaded...');

            triggerUploadStateChange(uploadDocument, DOCUMENT_UPLOAD_STATE.UPLOADING, {
                progress: 20,
            });
            rerender(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );
            expect(getProgressBarValue(uploadDocument)).toEqual(20);
            expect(getProgressText(uploadDocument)).toContain('20% uploaded...');

            triggerUploadStateChange(uploadDocument, DOCUMENT_UPLOAD_STATE.SUCCEEDED, {
                progress: 100,
            });
            rerender(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );
            expect(getProgressBarValue(uploadDocument)).toEqual(100);
            expect(getProgressText(uploadDocument)).toContain('Upload succeeded');
        });

        it('renders a retry upload button when first attempt fails that reuploads document', () => {
            const uploadDocument = {
                file: buildTextFile('one', 100),
                state: DOCUMENT_UPLOAD_STATE.FAILED,
                id: '1',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 1,
            };

            const uploadSession = buildUploadSession([uploadDocument]);
            render(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );

            expect(getProgressBarValue(uploadDocument)).toEqual(0);
            expect(getProgressText(uploadDocument)).toContain('Upload failed');
            expect(screen.getByRole('button', { name: 'Retry upload' })).toBeInTheDocument();

            userEvent.click(screen.getByRole('button', { name: 'Retry upload' }));
            expect(mockUploadAndScan).toHaveBeenCalled();
        });

        it('renders a warning callout to retry failed document uploads', () => {
            const uploadDocument = {
                file: buildTextFile('one', 100),
                state: DOCUMENT_UPLOAD_STATE.FAILED,
                id: '1',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 1,
            };

            const uploadSession = buildUploadSession([uploadDocument]);

            render(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );

            const warningStrings = [
                'There is a problem with some of your files',
                'Some of your files failed to upload',
                'You cannot continue until you retry uploading these files',
                'Retry uploading all failed files',
            ];
            warningStrings.forEach((s) => {
                const st = new RegExp(s, 'i');
                expect(screen.getByText(st)).toBeInTheDocument();
            });
            userEvent.click(screen.getByRole('link', { name: 'Retry uploading all failed files' }));
            expect(mockUploadAndScan).toHaveBeenCalled();
        });
    });

    describe.skip('Accessibility', () => {
        it('pass accessibility checks during upload', async () => {
            const uploadDocument = {
                file: buildTextFile('one', 100),
                state: DOCUMENT_UPLOAD_STATE.UPLOADING,
                id: '1',
                progress: 50,
                docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                attempts: 0,
            };

            const uploadSession = buildUploadSession([uploadDocument]);
            render(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when some files failed and warning callout appeared', async () => {
            const uploadDocument = {
                file: buildTextFile('one', 100),
                state: DOCUMENT_UPLOAD_STATE.FAILED,
                id: '1',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 10,
            };

            const uploadSession = buildUploadSession([uploadDocument]);
            render(
                <LloydGeorgeUploadStage
                    documents={[uploadDocument]}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={mockUploadAndScan}
                    nhsNumber={nhsNumber}
                />,
            );

            await screen.findByText('There is a problem with some of your files');
            await screen.findByText('File failed to upload');

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    afterEach(() => {
        cleanup();
    });
});
