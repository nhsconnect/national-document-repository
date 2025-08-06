import { render, waitFor, screen } from '@testing-library/react';
import DocumentUploadCompleteStage from './DocumentUploadCompleteStage';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';
import { LinkProps } from 'react-router-dom';

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));

URL.createObjectURL = vi.fn();

describe('DocumentUploadCompleteStage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders', async () => {
        render(<DocumentUploadCompleteStage />);

        await waitFor(async () => {
            expect(
                screen.getByText(
                    'You have successfully uploaded a digital Lloyd George record for:',
                ),
            ).toBeInTheDocument();
        });
    });

    it('should navigate to search when clicking the search link', async () => {
        render(<DocumentUploadCompleteStage />);

        await userEvent.click(screen.getByTestId('search-patient-link'));

        await waitFor(async () => {
            expect(mockNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
        });
    });

    it('should navigate to home when clicking the got to home button', async () => {
        render(<DocumentUploadCompleteStage />);

        await userEvent.click(screen.getByTestId('home-btn'));

        await waitFor(async () => {
            expect(mockNavigate).toHaveBeenCalledWith(routes.HOME);
        });
    });
});
