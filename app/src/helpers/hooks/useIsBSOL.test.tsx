import { render, screen } from '@testing-library/react';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../test/testBuilders';
import useIsBSOL from './useIsBSOL';

describe('useIsBSOL', () => {
    beforeEach(() => {
        sessionStorage.setItem('UserSession', '');
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('returns true when user has a session with isBSOL set to true', () => {
        renderHook(true);
        expect(screen.getByText(`isBSOL: true`)).toBeInTheDocument();
    });

    it('returns null when there is no session', () => {
        renderHook();
        expect(screen.getByText(`isBSOL: null`)).toBeInTheDocument();
    });
});

const TestApp = () => {
    const isBSOL = useIsBSOL();
    return <div>{`isBSOL: ${isBSOL}`.normalize()}</div>;
};

const renderHook = (isBSOL?: boolean) => {
    const session: Session = {
        auth: buildUserAuth({ isBSOL }),
        isLoggedIn: true,
    };
    return render(
        <SessionProvider sessionOverride={isBSOL ? session : undefined}>
            <TestApp />
        </SessionProvider>,
    );
};
