import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { buildPatientDetails, buildTextFile } from '../../../../helpers/test/testBuilders';
import CompleteStage from './CompleteStage';
import { useNavigate } from 'react-router-dom';
import usePatient from '../../../../helpers/hooks/usePatient';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('react-router-dom');
vi.mock('../../../../helpers/hooks/usePatient');

const mockedUsePatient = usePatient as Mock;
const mockPatientDetails = buildPatientDetails();

describe('<CompleteStage />', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatientDetails);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Show complete stage', () => {
        it('with successfully uploaded docs', async () => {
            const navigateMock = vi.fn();
            const documentOne: UploadDocument = {
                file: buildTextFile('one', 100),
                progress: 0,
                state: documentUploadStates.FAILED,
                id: '1',
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };
            const documentTwo: UploadDocument = {
                file: buildTextFile('two', 200),
                progress: 0,
                state: documentUploadStates.SUCCEEDED,
                id: '2',
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };
            const documentThree: UploadDocument = {
                file: buildTextFile('three', 100),
                progress: 0,
                state: documentUploadStates.SUCCEEDED,
                id: '3',
                docType: DOCUMENT_TYPE.ARF,
                attempts: 0,
            };

            // @ts-ignore
            useNavigate.mockImplementation(() => navigateMock);
            const documents: Array<UploadDocument> = [documentOne, documentTwo, documentThree];
            render(<CompleteStage documents={documents} />);
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

    it('pass accessibility checks', async () => {
        render(<CompleteStage documents={[]} />);
        expect(await screen.findByRole('heading', { name: 'Upload Summary' })).toBeInTheDocument();

        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });
});
