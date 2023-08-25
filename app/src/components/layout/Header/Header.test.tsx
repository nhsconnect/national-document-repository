import { render, screen, within } from '@testing-library/react';
import Header from './Header';
import { routes } from '../../../types/generic/routes';
import { Router } from 'react-router';
import userEvent from '@testing-library/user-event';
import { useNavigate } from 'react-router';
import { createMemoryHistory } from 'history';

const mockNavigate = useNavigate as jest.Mock<typeof useNavigate>;
const history = createMemoryHistory({
  initialEntries: ['/', '/example'],
  initialIndex: 1
});

describe('Header', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('default rendering', () => {
    it('renders the header', () => {
      render(<Header />);

      expect(screen.getByRole('banner')).toBeInTheDocument();
    });

    it('renders a logo that navigates to the home path', () => {
      // const nhsLogoLink = screen.getByRole('link', { name: 'NHS homepage' });
      // expect(nhsLogoLink).toHaveAttribute('href', routes.HOME);
      // expect(
      //   within(nhsLogoLink).getByRole('img', { name: 'NHS Logo' })
      // ).toBeInTheDocument();

      const mockUseNavigate = jest.fn();
      mockNavigate.mockImplementation(() => mockUseNavigate);
      renderHeaderWithRouter();
      userEvent.click(screen.getByRole('img', { name: 'NHS Logo' }));

      expect(mockNavigate).toHaveBeenCalledWith(routes.HOME);
    });

    it('renders a service name that navigates to the home path', () => {
      const mockUseNavigate = jest.fn();
      mockNavigate.mockImplementation(() => mockUseNavigate);
      renderHeaderWithRouter();

      userEvent.click(
        screen.getByRole('heading', {
          name: 'Inactive Patient Record Administration'
        })
      );

      expect(mockNavigate).toHaveBeenCalledWith(routes.HOME);
    });

    it('renders a nav', () => {
      render(<Header />);

      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });
  });
});

const renderHeaderWithRouter = () => {
  render(
    <Router navigator={history} location={'/example'}>
      <Header />
    </Router>
  );
};
