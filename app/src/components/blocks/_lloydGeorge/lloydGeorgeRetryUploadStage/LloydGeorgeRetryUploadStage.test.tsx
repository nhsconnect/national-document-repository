import { render, screen } from '@testing-library/react';
import LloydGeorgeRetryUploadStage from './LloydGeorgeRetryUploadStage';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { describe, expect, it, vi } from 'vitest';

const mockUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockUseNavigate,
}));

describe.skip('LloydGeorgeRetryUploadStage', () => {
    describe('Rendering', () => {
        it('renders component', () => {
            render(<LloydGeorgeRetryUploadStage />);

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
                    name: 'NHS National Service Desk - this link will open in a new tab',
                }),
            ).toHaveAttribute(
                'href',
                'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
            );
        });
    });

    describe('Accessibility', () => {
        it('pass accessibility checks', async () => {
            render(<LloydGeorgeRetryUploadStage />);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates to file input stage when try again is clicked', () => {
            render(<LloydGeorgeRetryUploadStage />);

            expect(screen.getByRole('button', { name: 'Try upload again' })).toBeInTheDocument();
            userEvent.click(screen.getByRole('button', { name: 'Try upload again' }));
            expect(mockUseNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE_UPLOAD);
        });

        it('navigates to patient search when search patient is clicked', () => {
            render(<LloydGeorgeRetryUploadStage />);

            expect(
                screen.getByRole('button', { name: 'Search for a patient' }),
            ).toBeInTheDocument();
            userEvent.click(screen.getByRole('button', { name: 'Search for a patient' }));
            expect(mockUseNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
        });
    });
});
