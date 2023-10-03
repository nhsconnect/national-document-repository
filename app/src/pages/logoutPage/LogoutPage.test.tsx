import { render, screen, waitFor } from '@testing-library/react';
import LogoutPage from './LogoutPage';
import { useNavigate } from 'react-router';
import logout from '../../helpers/requests/logout';
import { routes } from '../../types/generic/routes';
const mockNavigate = useNavigate as jest.Mock<typeof useNavigate>;

jest.mock('../../providers/sessionProvider/SessionProvider', () => ({
    useSessionContext: jest.fn(),
}));

// describe('logoutPage', () => {
//     it('Displays a spinner', () => {
//         render(<LogoutPage />);

//         expect(screen.getByRole('Spinner').toBeInTheDocument());
//     });
//     it('Makes a call to the logout endpoint', async () => {
//         await render(<LogoutPage />);
//         expect(logout).toHaveBeenCalled();
//         expect(screen.getByRole('Spinner').toBeInTheDocument());
//     });
//     it('Clears the local session and forwards the user to the start page when a 200 response is recieved', async () => {
//         const mockNavigate = jest.fn();
//         const mockUseNavigate = jest.fn();
//         useSessionContext.mockReturnValue([{}, setSessionMock]);
//         mockNavigate.mockImplementation(() => mockUseNavigate);

//         await render(<LogoutPage />);

//         expect(setSessionMock).toHaveBeenCalledWith({
//             auth: null,
//             isLoggedIn: false,
//         });

//         expect(useNavigate).toHaveBeenCalledWith(routes.HOME);
//     });
// });
