import { render, screen } from '@testing-library/react';
import LloydGeorgeRetryUploadStage from './LloydGeorgeRetryUploadStage';
import userEvent from '@testing-library/user-event';
import { LG_UPLOAD_STAGE } from '../../../pages/lloydGeorgeUploadPage/LloydGeorgeUploadPage';
import { routes } from '../../../types/generic/routes';

const mockSetStage = jest.fn();
const mockUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockUseNavigate,
}));

describe('LloydGeorgeRetryUploadStage', () => {
    describe('Rendering', () => {
        it('renders component', () => {
            render(<LloydGeorgeRetryUploadStage setStage={mockSetStage} />);

            const contentStrings = [
                'The record did not upload',
                'One or more files failed to upload, which prevented the full record being uploaded',
                'The Lloyd George record was not uploaded for this patient. You will need to check your files and try again',
                "Make sure to safely store the full digital or paper Lloyd George record until it's completely uploaded to this storage.",
                'Contact the',
                'if this issue continues',
            ];
            contentStrings.forEach((s) => {
                const st = new RegExp(s, 'i');
                expect(screen.getByText(st)).toBeInTheDocument();
            });
            expect(
                screen.getByRole('link', {
                    name: '(NHS National Service Desk - this link will open in a new tab)',
                }),
            ).toHaveAttribute(
                'href',
                'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
            );
        });
    });

    describe('Navigation', () => {
        it('navigates to file input stage when try again is clicked', () => {
            render(<LloydGeorgeRetryUploadStage setStage={mockSetStage} />);

            expect(screen.getByRole('button', { name: 'Try upload again' })).toBeInTheDocument();
            userEvent.click(screen.getByRole('button', { name: 'Try upload again' }));
            expect(mockSetStage).toHaveBeenCalledWith(LG_UPLOAD_STAGE.SELECT);
        });

        it('navigates to patient search when search patient is clicked', () => {
            render(<LloydGeorgeRetryUploadStage setStage={mockSetStage} />);

            expect(
                screen.getByRole('button', { name: 'Search for a patient' }),
            ).toBeInTheDocument();
            userEvent.click(screen.getByRole('button', { name: 'Search for a patient' }));
            expect(mockUseNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
        });
    });
});
