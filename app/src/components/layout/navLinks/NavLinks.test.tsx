import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import NavLinks from './NavLinks';

describe('NavLinks', () => {
    const oldWindowLocation = window.location;

    afterEach(() => {
        jest.clearAllMocks();
        window.location = oldWindowLocation;
    });

    it('renders a navlink that returns to app home', () => {
        renderNavWithRouter();

        expect(screen.getByRole('link', { name: 'Home' })).toBeInTheDocument();
    });
});

const renderNavWithRouter = () => {
    render(
        <MemoryRouter>
            <NavLinks />
        </MemoryRouter>,
    );
};
