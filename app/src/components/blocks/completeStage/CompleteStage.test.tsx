import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import { buildPatientDetails, buildTextFile } from '../../../helpers/test/testBuilders';
import CompleteStage from './CompleteStage';
import { useNavigate } from 'react-router';

jest.mock('react-router');
const mockPatientDetails = buildPatientDetails();
describe('<CompleteStage />', () => {
    describe('Show complete stage', () => {
        it('with successfully uploaded docs', async () => {
            const navigateMock = jest.fn();
            const documentOne: UploadDocument = {
                file: buildTextFile('one', 100),
                progress: 0,
                state: documentUploadStates.FAILED,
                id: '1',
                docType: DOCUMENT_TYPE.ARF,
            };
            const documentTwo: UploadDocument = {
                file: buildTextFile('two', 200),
                progress: 0,
                state: documentUploadStates.SUCCEEDED,
                id: '2',
                docType: DOCUMENT_TYPE.ARF,
            };
            const documentThree: UploadDocument = {
                file: buildTextFile('three', 100),
                progress: 0,
                state: documentUploadStates.SUCCEEDED,
                id: '3',
                docType: DOCUMENT_TYPE.ARF,
            };

            // @ts-ignore
            useNavigate.mockImplementation(() => navigateMock);
            const documents: Array<UploadDocument> = [documentOne, documentTwo, documentThree];
            render(<CompleteStage patientDetails={mockPatientDetails} documents={documents} />);
            expect(
                await screen.findByRole('heading', { name: 'Upload Summary' }),
            ).toBeInTheDocument();

            userEvent.click(screen.getByLabelText('View successfully uploaded documents'));

            expect(screen.getByText(documentTwo.file.name)).toBeInTheDocument();
            expect(screen.getByText(documentThree.file.name)).toBeInTheDocument();
            expect(screen.getByRole('heading', { name: 'There is a problem' })).toBeInTheDocument();
            expect(screen.getByText(`1 of 3 files failed to upload`)).toBeInTheDocument();
            expect(
                screen.getByText("If you want to upload another patient's health record"),
            ).toBeInTheDocument();

            userEvent.click(screen.getByRole('button', { name: 'Start Again' }));

            expect(navigateMock).toHaveBeenCalledWith('/');
        });
    });
});
