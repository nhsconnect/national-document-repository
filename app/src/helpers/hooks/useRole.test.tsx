import { render, screen } from '@testing-library/react';
import { REPOSITORY_ROLE, authorisedRoles } from '../../types/generic/authRole';
import useRole from './useRole';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../test/testBuilders';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

describe('useRole', () => {
    beforeEach(() => {
        localStorage.setItem('UserSession', '');
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it.each(authorisedRoles)(
        "returns a role when there is an authorised session for user role '%s'",
        async (role) => {
            renderHook(role);
            expect(screen.getByText(`ROLE: ${role}`)).toBeInTheDocument();
        },
    );

    it('returns null when there is no session', () => {
        renderHook();
        expect(screen.getByText(`ROLE: null`)).toBeInTheDocument();
    });
});

const TestApp = () => {
    const role = useRole();
    return <div>{`ROLE: ${role}`.normalize()}</div>;
};

const renderHook = (role?: REPOSITORY_ROLE) => {
    const session: Session = {
        auth: buildUserAuth({ role }),
        isLoggedIn: true,
    };
    return render(
        <SessionProvider sessionOverride={role ? session : undefined}>
            <TestApp />
        </SessionProvider>,
    );
};
