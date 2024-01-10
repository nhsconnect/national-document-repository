import { render, screen } from '@testing-library/react';
import HomePage from './StartPage';
import { useNavigate } from 'react-router';

jest.mock('react-router');
const mockNavigate = useNavigate as jest.Mock<typeof useNavigate>;

describe('StartPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header', () => {
        const mockUseNavigate = jest.fn();
        mockNavigate.mockImplementation(() => mockUseNavigate);

        render(<HomePage />);

        expect(
            screen.getByRole('heading', {
                name: 'Access and store digital GP records',
            }),
        ).toBeInTheDocument();
    });

    it('renders home page content', () => {
        const mockNavigate = jest.fn();
        const mockUseNavigate = jest.fn();
        mockNavigate.mockImplementation(() => mockUseNavigate);

        const contentStrings = [
            'This service gives you access to Lloyd George digital health records. ' +
                'You may have received a note within a patient record, stating that the record has been digitised.',
            'If you are part of a GP practice, you can use this service to:',
            'view a patient record',
            'remove a patient record',
            'If you are managing records on behalf of NHS England, you can:',
            'Not every patient will have a digital record available.',
            'Before you start',
            'You’ll be asked for:',
            'your NHS smartcard',
            'patient details including their name, date of birth and NHS number',
        ];

        render(<HomePage />);

        contentStrings.forEach((s) => {
            expect(screen.getByText(s)).toBeInTheDocument();
        });

        const downloadPatientRecord = screen.getAllByText('download a patient record');
        expect(downloadPatientRecord).toHaveLength(2);

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
});
