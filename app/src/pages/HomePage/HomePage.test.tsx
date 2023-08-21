import { render, screen } from '@testing-library/react';
import HomePage from './index';
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
        name: 'Inactive Patient Record Administration'
      })
    ).toBeInTheDocument();
  });

  it('renders service info', () => {
    const mockNavigate = jest.fn();
    const mockUseNavigate = jest.fn();
    mockNavigate.mockImplementation(() => mockUseNavigate);

    render(<HomePage />);

    expect(screen.getByText(/When a patient is inactive/)).toBeInTheDocument();
    expect(screen.getByText(/General Practice Staff/)).toBeInTheDocument();
    expect(
      screen.getByText(/PCSE should use this service/)
    ).toBeInTheDocument();
  });

  it('renders service issue guidance with a link to service desk that opens in a new tab', () => {
    const mockUseNavigate = jest.fn();
    mockNavigate.mockImplementation(() => mockUseNavigate);

    render(<HomePage />);

    expect(screen.getByText(/If there is an issue/)).toBeInTheDocument();
    const nationalServiceDeskLink = screen.getByRole('link', {
      name: /National Service Desk/
    });
    expect(nationalServiceDeskLink).toHaveAttribute(
      'href',
      'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks'
    );
    expect(nationalServiceDeskLink).toHaveAttribute('target', '_blank');
  });

  it("renders a 'Before you start' section", () => {
    const mockUseNavigate = jest.fn();
    mockNavigate.mockImplementation(() => mockUseNavigate);

    render(<HomePage />);

    expect(
      screen.getByRole('heading', { name: 'Before You Start' })
    ).toBeInTheDocument();
    expect(screen.getByText(/valid NHS smartcard/)).toBeInTheDocument();
  });
});
