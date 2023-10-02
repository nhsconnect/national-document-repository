import { createContext, useContext, useEffect, useState } from 'react';
import type { Dispatch, ReactNode, SetStateAction } from 'react';
import { UserAuth } from '../../types/blocks/userAuth';

type Props = {
    children: ReactNode;
    sessionOverride?: Partial<Session>;
};
export type Session = {
    auth: UserAuth | null;
    isLoggedIn: boolean;
    sessionOverride?: Partial<Session>;
};

export type SessionContext = [Session, Dispatch<SetStateAction<Session>>];

const UserSessionContext = createContext<SessionContext | null>(null);
const SessionProvider = ({ children, sessionOverride }: Props) => {
    const emptyAuth = { auth: null, isLoggedIn: false, ...sessionOverride };

    const storedAuth = sessionStorage.getItem('UserSession');
    const auth: Session = storedAuth ? JSON.parse(storedAuth) : emptyAuth;
    const [session, setSession] = useState<Session>({
        ...auth,
        sessionOverride,
    });

    useEffect(() => {
        sessionStorage.setItem('UserSession', JSON.stringify(session) ?? emptyAuth);
    }, [session]);

    return (
        <UserSessionContext.Provider value={[session, setSession]}>
            {children}
        </UserSessionContext.Provider>
    );
};

export default SessionProvider;
export const useSessionContext = () => useContext(UserSessionContext) as SessionContext;
