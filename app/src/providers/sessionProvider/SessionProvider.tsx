import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { Dispatch, ReactNode, SetStateAction } from 'react';
import { UserAuth } from '../../types/blocks/userAuth';

type SetSessionOverride = (session: Session) => void;

type Props = {
    children: ReactNode;
    sessionOverride?: Partial<Session>;
    setSessionOverride?: SetSessionOverride;
};
export type Session = {
    auth: UserAuth | null;
    isLoggedIn: boolean;
    sessionOverride?: Partial<Session>;
};

export type SessionContext = [Session, Dispatch<SetStateAction<Session>> | SetSessionOverride];

const UserSessionContext = createContext<SessionContext | null>(null);
const SessionProvider = ({ children, sessionOverride, setSessionOverride }: Props) => {
    const emptyAuth = useMemo(
        () => ({ auth: null, isLoggedIn: false, ...sessionOverride }),
        [sessionOverride],
    );

    const storedAuth = sessionStorage.getItem('UserSession');
    const auth: Session = storedAuth ? JSON.parse(storedAuth) : emptyAuth;
    const [session, setSession] = useState<Session>({
        ...auth,
        sessionOverride,
    });

    useEffect(() => {
        sessionStorage.setItem('UserSession', JSON.stringify(session) ?? emptyAuth);
    }, [session, emptyAuth]);

    return (
        <UserSessionContext.Provider value={[session, setSessionOverride ?? setSession]}>
            {children}
        </UserSessionContext.Provider>
    );
};

export default SessionProvider;
export const useSessionContext = () => useContext(UserSessionContext) as SessionContext;
