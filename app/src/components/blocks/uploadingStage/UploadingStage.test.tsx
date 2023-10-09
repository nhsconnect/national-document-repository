import { render, screen } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import {
    buildPatientDetails,
    buildTextFile,
    buildUserAuth,
} from '../../../helpers/test/testBuilders';
import UploadingStage from './UploadingStage';
import { createMemoryHistory } from 'history';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import { PatientDetails } from '../../../types/generic/patientDetails';
import PatientDetailsProvider from '../../../providers/patientProvider/PatientProvider';

jest.mock('react-router');
const mockPatient = buildPatientDetails();

describe('<UploadDocumentsPage />', () => {
    describe('with NHS number', () => {
        const triggerUploadStateChange = (
            document: UploadDocument,
            state: DOCUMENT_UPLOAD_STATE,
            progress: number
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
            };
            const documentTwo = {
                file: buildTextFile('two', 200),
                state: documentUploadStates.SELECTED,
                id: '2',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
            };
            const documentThree = {
                file: buildTextFile('three', 100),
                state: documentUploadStates.SELECTED,
                id: '3',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
            };

            renderUploadingStage([documentOne, documentTwo, documentThree]);

            triggerUploadStateChange(documentOne, documentUploadStates.UPLOADING, 0);

            expect(screen.queryByTestId('upload-document-form')).not.toBeInTheDocument();
            expect(
                screen.getByText(
                    'Do not close or navigate away from this browser until upload is complete.'
                )
            ).toBeInTheDocument();
        });

        it('progress bar reflect the upload progress', async () => {
            const documentOne = {
                file: buildTextFile('one', 100),
                state: documentUploadStates.SELECTED,
                id: '1',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
            };
            const documentTwo = {
                file: buildTextFile('two', 200),
                state: documentUploadStates.SELECTED,
                id: '2',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
            };
            const documentThree = {
                file: buildTextFile('three', 100),
                state: documentUploadStates.SELECTED,
                id: '3',
                progress: 0,
                docType: DOCUMENT_TYPE.ARF,
            };

            const { rerender } = render(
                <UploadingStage
                    patientDetails={mockPatient}
                    documents={[documentOne, documentTwo, documentThree]}
                />
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
            rerender(
                <UploadingStage
                    patientDetails={mockPatient}
                    documents={[documentOne, documentTwo, documentThree]}
                />
            );
            expect(getProgressBarValue(documentOne)).toEqual(10);
            expect(getProgressText(documentOne)).toContain('10% uploaded...');

            triggerUploadStateChange(documentOne, documentUploadStates.UPLOADING, 70);
            rerender(
                <UploadingStage
                    patientDetails={mockPatient}
                    documents={[documentOne, documentTwo, documentThree]}
                />
            );
            expect(getProgressBarValue(documentOne)).toEqual(70);
            expect(getProgressText(documentOne)).toContain('70% uploaded...');

            triggerUploadStateChange(documentTwo, documentUploadStates.UPLOADING, 20);
            rerender(
                <UploadingStage
                    patientDetails={mockPatient}
                    documents={[documentOne, documentTwo, documentThree]}
                />
            );
            expect(getProgressBarValue(documentTwo)).toEqual(20);
            expect(getProgressText(documentTwo)).toContain('20% uploaded...');

            triggerUploadStateChange(documentTwo, documentUploadStates.SUCCEEDED, 100);
            rerender(
                <UploadingStage
                    patientDetails={mockPatient}
                    documents={[documentOne, documentTwo, documentThree]}
                />
            );
            expect(getProgressBarValue(documentTwo)).toEqual(100);
            expect(getProgressText(documentTwo)).toContain('Uploaded');

            triggerUploadStateChange(documentOne, documentUploadStates.FAILED, 0);
            rerender(
                <UploadingStage
                    patientDetails={mockPatient}
                    documents={[documentOne, documentTwo, documentThree]}
                />
            );
            expect(getProgressBarValue(documentOne)).toEqual(0);
            expect(getProgressText(documentOne)).toContain('Upload failed');
        });
    });
});

const homeRoute = '/example';
const renderUploadingStage = (
    documents: Array<UploadDocument>,
    patientOverride: Partial<PatientDetails> = {},
    history = createMemoryHistory({
        initialEntries: [homeRoute],
        initialIndex: 1,
    })
) => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };
    const patient: PatientDetails = {
        ...buildPatientDetails(),
        ...patientOverride,
    };
    render(
        <SessionProvider sessionOverride={auth}>
            <PatientDetailsProvider patientDetails={patient}>
                <UploadingStage patientDetails={mockPatient} documents={documents} />
            </PatientDetailsProvider>
        </SessionProvider>
    );
};
