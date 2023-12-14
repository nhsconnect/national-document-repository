import { REPOSITORY_ROLE } from '../generic/authRole';

export type UserAuth = {
    role: REPOSITORY_ROLE;
    authorisation_token: string;
    isBSOL: boolean;
};
