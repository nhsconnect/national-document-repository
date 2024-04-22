import { render, screen } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { buildTextFile } from '../../../../helpers/test/testBuilders';
import UploadingStage from './UploadingStage';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';

describe('<UploadDocumentsPage />', () => {
    describe('with NHS number', () => {
        const triggerUploadStateChange = (
            document: UploadDocument,
            state: DOCUMENT_UPLOAD_STATE,
            progress: number,
        ) => {
            act(() => {
                document.state = state;
                document.progress = progress;
            });
        };

        it('uploads documents and displays the progress', async () => {
            const documentOne = {
                file: buildTextFile('one', 100),
                state: documentUploadStates.SELECTED,
                id: '1',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };
            const documentTwo = {
                file: buildTextFile('two', 200),
                state: documentUploadStates.SELECTED,
                id: '2',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };
            const documentThree = {
                file: buildTextFile('three', 100),
                state: documentUploadStates.SELECTED,
                id: '3',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };
            render(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);

            triggerUploadStateChange(documentOne, documentUploadStates.UPLOADING, 0);

            expect(screen.queryByTestId('upload-document-form')).not.toBeInTheDocument();
            expect(
                screen.getByText(
                    'Do not close or navigate away from this browser until upload is complete.',
                ),
            ).toBeInTheDocument();
        });

        it('progress bar reflect the upload progress', async () => {
            const documentOne = {
                file: buildTextFile('one', 100),
                state: documentUploadStates.SELECTED,
                id: '1',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };
            const documentTwo = {
                file: buildTextFile('two', 200),
                state: documentUploadStates.SELECTED,
                id: '2',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };
            const documentThree = {
                file: buildTextFile('three', 100),
                state: documentUploadStates.SELECTED,
                id: '3',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };

            const { rerender } = render(
                <UploadingStage documents={[documentOne, documentTwo, documentThree]} />,
            );
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

            triggerUploadStateChange(documentOne, documentUploadStates.UPLOADING, 10);
            rerender(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);
            expect(getProgressBarValue(documentOne)).toEqual(10);
            expect(getProgressText(documentOne)).toContain('10% uploaded...');

            triggerUploadStateChange(documentOne, documentUploadStates.UPLOADING, 70);
            rerender(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);
            expect(getProgressBarValue(documentOne)).toEqual(70);
            expect(getProgressText(documentOne)).toContain('70% uploaded...');

            triggerUploadStateChange(documentTwo, documentUploadStates.UPLOADING, 20);
            rerender(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);
            expect(getProgressBarValue(documentTwo)).toEqual(20);
            expect(getProgressText(documentTwo)).toContain('20% uploaded...');

            triggerUploadStateChange(documentTwo, documentUploadStates.SUCCEEDED, 100);
            rerender(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);
            expect(getProgressBarValue(documentTwo)).toEqual(100);
            expect(getProgressText(documentTwo)).toContain('Uploaded');

            triggerUploadStateChange(documentOne, documentUploadStates.FAILED, 0);
            rerender(<UploadingStage documents={[documentOne, documentTwo, documentThree]} />);
            expect(getProgressBarValue(documentOne)).toEqual(0);
            expect(getProgressText(documentOne)).toContain('Upload failed');
        });
    });

    it('pass accessibility check', async () => {
        const documentOne = {
            file: buildTextFile('one', 100),
            state: documentUploadStates.UPLOADING,
            id: '1',
            progress: 10,
            docType: DOCUMENT_TYPE.ARF,
            attempts: 0,
        };
        render(<UploadingStage documents={[documentOne]} />);

        await screen.findByText(documentOne.file.name);

        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });
});
