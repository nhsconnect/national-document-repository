import { getByText, render, screen, waitFor } from '@testing-library/react';
import MockCis2LoginPage from './MockCis2LoginPage';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import axios from 'axios';
import { routes } from '../../types/generic/routes';
import { afterEach, beforeEach, describe, expect, it, vi, Mocked } from 'vitest';
import StartPage from '../startPage/StartPage';

vi.mock('axios');
const mockedAxios = axios as Mocked<typeof axios>;
const mockSetSession = vi.fn();
const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('MockCis2LoginPage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders a username and password fields', () => {
        renderMockCis2LoginPage();
        expect(screen.getByText('Username')).toBeInTheDocument();
        expect(screen.getByRole('textbox', { name: 'Username' })).toBeInTheDocument();
        expect(screen.getByText('Password')).toBeInTheDocument();
        expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });

    it('renders a continue button', () => {
        renderMockCis2LoginPage();
        expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();
    });
});

const renderMockCis2LoginPage = () => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: false,
    };
    render(
        <SessionProvider sessionOverride={auth} setSessionOverride={mockSetSession}>
            <MockCis2LoginPage />
        </SessionProvider>,
    );
};
