import { render, waitFor, screen } from '@testing-library/react';
import DocumentSelectOrderStage from './DocumentSelectOrderStage';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import DocumentSelectStage from '../documentSelectStage/DocumentSelectStage';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

const patientDetails = buildPatientDetails();

URL.createObjectURL = vi.fn();

describe('DocumentSelectOrderStage', () => {
    let documents: UploadDocument[] = [];
    beforeEach(() => {
        vi.mocked(usePatient).mockReturnValue(patientDetails);

        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        documents = [
            {
                docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                id: '1',
                file: new Blob() as File,
                attempts: 0,
                state: DOCUMENT_UPLOAD_STATE.SELECTED,
            },
        ];
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders', async () => {
            renderSut(documents);

            await waitFor(async () => {
                expect(
                    screen.getByText('Your files are not currently in order:'),
                ).toBeInTheDocument();
            });
        });
    });

    it('renders patient summary fields is inset', async () => {
        renderSut(documents);

        const insetText = screen
            .getByText('Make sure that all files uploaded are for this patient only:')
            .closest('.nhsuk-inset-text');
        expect(insetText).toBeInTheDocument();

        const expectedFullName = `${patientDetails.familyName}, ${patientDetails.givenName}`;
        expect(screen.getByText(/Patient name/i)).toBeInTheDocument();
        expect(screen.getByText(expectedFullName)).toBeInTheDocument();

        expect(screen.getByText(/NHS number/i)).toBeInTheDocument();
        const expectedNhsNumber = formatNhsNumber(patientDetails.nhsNumber);
        expect(screen.getByText(expectedNhsNumber)).toBeInTheDocument();

        expect(screen.getByText(/Date of birth/i)).toBeInTheDocument();
        const expectedDob = getFormattedDate(new Date(patientDetails.birthDate));
        expect(screen.getByText(expectedDob)).toBeInTheDocument();
    });
});

function renderSut(documents: UploadDocument[]) {
    render(
        <DocumentSelectStage
            documents={documents}
            setDocuments={() => {}}
            documentType={DOCUMENT_TYPE.LLOYD_GEORGE}
        />,
    );
}
