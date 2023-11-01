import { AUTH_ROLE } from '../generic/authRole';

export type UserAuth = {
    role: AUTH_ROLE;
    authorisation_token: string;
};
