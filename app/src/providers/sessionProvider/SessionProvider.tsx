import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode, SetStateAction, Dispatch } from 'react';
import { UserAuth } from '../../types/blocks/userAuth';

type Props = {
    children: ReactNode;
};
type Session = {
    auth: UserAuth | null;
    isLoggedIn: boolean;
};

export type SessionContext = [Session, Dispatch<SetStateAction<Session>>, () => void];

const UserSessionContext = createContext<SessionContext | null>(null);
const SessionProvider = ({ children }: Props) => {
    const storedAuth = sessionStorage.getItem('UserAuth');
    const auth = storedAuth ? JSON.parse(storedAuth) : null;
    const isLoggedIn = sessionStorage.getItem('LoggedIn') === 'true';
    const [session, setSession] = useState<Session>({
        isLoggedIn,
        auth,
    });

    const deleteSession = () => {
        setSession({
            auth: null,
            isLoggedIn: false,
        });
    };

    useEffect(() => {
        sessionStorage.setItem('LoggedIn', session.isLoggedIn ? 'true' : 'false');
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
