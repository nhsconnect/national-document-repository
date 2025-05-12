import { render, screen } from '@testing-library/react';
import LloydGeorgeUploadInfectedStage from './LloydGeorgeUploadInfectedStage';
import { buildLgFile } from '../../../../helpers/test/testBuilders';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
} from '../../../../types/pages/UploadDocumentsPage/types';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { describe, expect, it, vi } from 'vitest';

const mockedUseNavigate = vi.fn();
const restartJourneyMock = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));
const uploadDocument = {
    file: buildLgFile(1, 1, 'John Doe'),
    state: DOCUMENT_UPLOAD_STATE.INFECTED,
    id: '1',
    progress: 0,
    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
    attempts: 1,
};

describe('LloydGeorgeUploadInfectedStage', () => {
    describe('Rendering', () => {
        it('renders infected warning when document has infected status', () => {
            const contentStrings = [
                'The record did not upload',
                'Some of your files failed a virus scan:',
                'This prevented the Lloyd George record being uploaded.',
                'You will need to check your files and try again.',
                'Make sure to safely store the full digital or paper Lloyd George',
                "record until it's completely uploaded to this storage.",
                'Contact the',
                'if this issue continues.',
            ];

            render(
                <LloydGeorgeUploadInfectedStage
                    documents={[uploadDocument]}
                    restartUpload={restartJourneyMock}
                />,
            );
            contentStrings.forEach((s) => {
                const st = new RegExp(s, 'i');
                expect(screen.getByText(st)).toBeInTheDocument();
            });
            expect(screen.getByText(uploadDocument.file.name)).toBeInTheDocument();

            expect(
                screen.getByRole('link', {
                    name: 'NHS National Service Desk - this link will open in a new tab',
                }),
            ).toHaveAttribute(
                'href',
                'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
            );

            expect(screen.getByRole('button', { name: 'Try upload again' })).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Search for a patient' }),
            ).toBeInTheDocument();
        });
    });

    describe.skip('Accessibility', () => {
        it('pass accessibility checks', async () => {
            render(
                <LloydGeorgeUploadInfectedStage
                    documents={[uploadDocument]}
                    restartUpload={restartJourneyMock}
                />,
            );
            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates to search for a patient page when button is clicked', () => {
            render(
                <LloydGeorgeUploadInfectedStage
                    documents={[uploadDocument]}
                    restartUpload={restartJourneyMock}
                />,
            );

            expect(
                screen.getByRole('button', { name: 'Search for a patient' }),
            ).toBeInTheDocument();
            userEvent.click(screen.getByRole('button', { name: 'Search for a patient' }));

            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
        });

        it('restarts to beginning of upload journey when button is clicked', () => {
            render(
                <LloydGeorgeUploadInfectedStage
                    documents={[uploadDocument]}
                    restartUpload={restartJourneyMock}
                />,
            );

            expect(screen.getByRole('button', { name: 'Try upload again' })).toBeInTheDocument();
            userEvent.click(screen.getByRole('button', { name: 'Try upload again' }));

            expect(restartJourneyMock).toHaveBeenCalled();
        });
    });
});
