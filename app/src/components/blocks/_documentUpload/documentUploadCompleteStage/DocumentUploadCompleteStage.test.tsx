import { render, waitFor, screen } from "@testing-library/react";
import DocumentUploadCompleteStage from "./DocumentUploadCompleteStage";

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

URL.createObjectURL = vi.fn();

describe('DocumentUploadCompleteStage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders', async () => {
            render(<DocumentUploadCompleteStage />);

            await waitFor(async () => {
                expect(
                    screen.getByText('You have successfully uploaded a digital Lloyd George record for:')
                ).toBeInTheDocument();
            });
        });
    });
});