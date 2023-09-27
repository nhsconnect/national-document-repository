import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { UserAuth } from '../../types/blocks/userAuth';

type Props = {
    children: ReactNode;
    sessionOverride?: Partial<Session>;
};
type Session = {
    auth: UserAuth | null;
    isLoggedIn: boolean;
};

export type SessionContext = [Session, (auth: UserAuth) => void, () => void];

const UserSessionContext = createContext<SessionContext | null>(null);
const SessionProvider = ({ children, sessionOverride }: Props) => {
    const storedAuth = sessionStorage.getItem('UserAuth');
    const auth: UserAuth | null = storedAuth ? JSON.parse(storedAuth) : null;
    const [session, setAuthSession] = useState<Session>({
        isLoggedIn: !!auth?.authorisation_token,
        auth,
        ...sessionOverride,
    });

    const deleteSession = () => {
        setAuthSession({
            auth: null,
            isLoggedIn: false,
        });
    };

    const setSession = (auth: UserAuth) => {
        setAuthSession({
            auth,
            isLoggedIn: !!auth?.authorisation_token,
        });
    };

    useEffect(() => {
        sessionStorage.setItem('UserAuth', JSON.stringify(session.auth) ?? null);
    }, [session]);

    return (
        <UserSessionContext.Provider value={[session, setSession, deleteSession]}>
            {children}
        </UserSessionContext.Provider>
    );
};

export default SessionProvider;
export const useSessionContext = () => useContext(UserSessionContext) as SessionContext;
