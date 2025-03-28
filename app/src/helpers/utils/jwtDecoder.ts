import { jwtDecode } from 'jwt-decode';

export const decodeJwtToken = <T>(token: string): T | null => {
    try {
        return jwtDecode<T>(token);
    } catch (error) {
        console.error('Invalid JWT token:', error); // eslint-disable-line
        return null;
    }
};
