import { getByText, render, screen, waitFor } from '@testing-library/react';
import MockCis2LoginPage from './MockRoleSelectPage';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import axios from 'axios';
import { routes } from '../../types/generic/routes';
import { afterEach, beforeEach, describe, expect, it, vi, Mocked } from 'vitest';
import StartPage from '../startPage/StartPage';
import MockRoleSelectPage from './MockRoleSelectPage';

vi.mock('axios');
const mockedAxios = axios as Mocked<typeof axios>;
const mockSetSession = vi.fn();
const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('MockRoleSelectPage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders a heading', () => {
        renderMockRoleSelectPage();
        expect(screen.getByRole('heading', { name: 'Select an organisation' })).toBeInTheDocument();
    });

    it('renders a continue button', () => {
        renderMockRoleSelectPage();
        expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();
    });
});

const renderMockRoleSelectPage = () => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };
    render(
        <SessionProvider sessionOverride={auth} setSessionOverride={mockSetSession}>
            <MockRoleSelectPage />
        </SessionProvider>,
    );
};
