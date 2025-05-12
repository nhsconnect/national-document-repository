import { render, waitFor } from '@testing-library/react';
import * as ReactRouter from 'react-router-dom';
import { History, createMemoryHistory } from 'history';
import { routeChildren, routes } from '../../../types/generic/routes';
import RoleGuard from './RoleGuard';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../helpers/hooks/useRole');
const mockedUseRole = useRole as Mock;

const guardPage = routes.LLOYD_GEORGE;
const childGuardPage = routeChildren.LLOYD_GEORGE_DOWNLOAD;

describe('RoleGuard', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });
    it('navigates user to unauthorised when role is not accepted', async () => {
        const history = createMemoryHistory({
            initialEntries: [guardPage],
            initialIndex: 0,
        });

        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
        expect(history.location.pathname).toBe(guardPage);
        renderAuthGuard(history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(routes.UNAUTHORISED);
        });
    });

    it('navigates user to correct page when role is accepted', async () => {
        const history = createMemoryHistory({
            initialEntries: [guardPage],
            initialIndex: 0,
        });

        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
        expect(history.location.pathname).toBe(guardPage);
        renderAuthGuard(history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(guardPage);
        });
    });

    it('navigates user to correct page when role is accepted using child route', async () => {
        const history = createMemoryHistory({
            initialEntries: [childGuardPage],
            initialIndex: 0,
        });

        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
        expect(history.location.pathname).toBe(childGuardPage);
        renderAuthGuard(history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(childGuardPage);
        });
    });
});

const renderAuthGuard = (history: History) => {
    return render(
        <ReactRouter.Router navigator={history} location={history.location}>
            <RoleGuard>
                <div />
            </RoleGuard>
        </ReactRouter.Router>,
    );
};
