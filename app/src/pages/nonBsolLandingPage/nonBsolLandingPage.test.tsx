import { render, screen } from '@testing-library/react';
import { useNavigate } from 'react-router';
import NonBsolLandingPage from './NonBsolLandingPage';
import HomePage from '../homePage/HomePage';

jest.mock('react-router');
const mockNavigate = useNavigate as jest.Mock<typeof useNavigate>;
//
describe('NonBsolLandingPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header', () => {
        renderNonBsolLandingPage();

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
            'Downloading a record will remove it from our storage',
            'Get support with the service',
        ];

        renderNonBsolLandingPage();

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
        const mockUseNavigate = jest.fn();
        mockNavigate.mockImplementation(() => mockUseNavigate);

        render(<HomePage />);

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

    it('renders a primary button that takes you to the search patient page', () => {
        const mockNavigateToNextPage = jest.fn();

        render(<NonBsolLandingPage next={mockNavigateToNextPage} />);

        const searchButton = screen.getByRole('button', { name: 'Search for a patient' });
        expect(searchButton).toBeInTheDocument();
    });
});

const renderNonBsolLandingPage = () => {
    render(<NonBsolLandingPage next={(e) => {}} />);
};
