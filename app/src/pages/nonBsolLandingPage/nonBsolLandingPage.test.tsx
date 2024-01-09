import { render, screen, waitFor } from '@testing-library/react';
import NonBsolLandingPage from './NonBsolLandingPage';
import { routes } from '../../types/generic/routes';

const mockedNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedNavigate,
}));

describe('NonBsolLandingPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header', () => {
        render(<NonBsolLandingPage />);

        expect(
            screen.getByRole('heading', {
                name: 'You’re outside of Birmingham and Solihull (BSOL)',
            }),
        ).toBeInTheDocument();
    });

    it('renders page content', () => {
        const contentStrings = [
            'As you’re outside Birmingham and Solihull, the pilot area for this service, you can use this service to:',
            'view records if the patient joins your practice',
            'download records if a patient leaves your practice',
            'You’ll be asked for patient details, including their:',
            'name',
            'date of birth',
            'NHS number',
            'Downloading a record will remove it from our storage.',
            'Get support with the service',
        ];

        render(<NonBsolLandingPage />);

        contentStrings.forEach((s) => {
            expect(screen.getByText(s)).toBeInTheDocument();
        });
        expect(screen.getByText(/Contact the/i)).toBeInTheDocument();
        expect(
            screen.getByRole('link', {
                name: /NHS National Service Desk/i,
            }),
        ).toBeInTheDocument();
        expect(
            screen.getByText(/if there is an issue with this service or call 0300 303 5678\./i),
        ).toBeInTheDocument();
    });

    it('renders a service link that takes you to service help-desk in a new tab', () => {
        render(<NonBsolLandingPage />);

        expect(screen.getByText(/Contact the/i)).toBeInTheDocument();
        const nationalServiceDeskLink = screen.getByRole('link', {
            name: /NHS National Service Desk/i,
        });
        expect(
            screen.getByText(/if there is an issue with this service or call 0300 303 5678/i),
        ).toBeInTheDocument();

        expect(nationalServiceDeskLink).toHaveAttribute(
            'href',
            'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
        );
        expect(nationalServiceDeskLink).toHaveAttribute('target', '_blank');
    });

    it('renders a primary button that takes user to the upload search patient page', async () => {
        render(<NonBsolLandingPage />);

        const button = screen.getByRole('button', { name: 'Search for a patient' });
        expect(button).toBeInTheDocument();

        button.click();

        await waitFor(() => {
            expect(mockedNavigate).toHaveBeenCalledWith(routes.UPLOAD_SEARCH);
        });
    });
});
