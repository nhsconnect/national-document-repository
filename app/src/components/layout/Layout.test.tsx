import { act, render, screen } from '@testing-library/react';
import Layout from './Layout';
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';
import userEvent from '@testing-library/user-event';

import { buildUserAuth } from '../../helpers/test/testBuilders';
import { runAxeTestForLayout } from '../../helpers/test/axeTestHelper';

describe('Layout', () => {
    beforeEach(() => {
        window.sessionStorage.clear();
    });
    describe('Accessibility', () => {
        it('pass accessibility checks when not logged in', async () => {
            renderTestApp('/', false);

            const results = await runAxeTestForLayout(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when logged in', async () => {
            renderTestApp('/', true);

            const results = await runAxeTestForLayout(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('SkipLink', () => {
        it('renders a skip link element', () => {
            renderTestApp();
            expect(screen.getByRole('link', { name: 'Skip to main content' })).toBeInTheDocument();
        });

        it('focus on the first h1 element when triggered', () => {
            renderTestApp();

            const skipLink = screen.getByRole('link', { name: 'Skip to main content' });
            const firstH1Heading = screen.getByRole('heading', { name: 'Test heading 1' });

            userEvent.tab();
            expect(skipLink).toHaveFocus();

            userEvent.keyboard('[Enter]');
            expect(firstH1Heading).toHaveFocus();
        });

        it('focus on the main element if there is no h1 heading in the page', () => {
            renderTestApp('/withoutSizeOneHeading');

            const skipLink = screen.getByRole('link', { name: 'Skip to main content' });
            const mainContent = screen.getByRole('main');

            userEvent.tab();
            expect(skipLink).toHaveFocus();

            userEvent.keyboard('[Enter]');
            expect(mainContent).toHaveFocus();
        });

        it('becomes the next focusable item when navigate to a new route', async () => {
            renderTestApp();

            const link = screen.getByRole('link', { name: 'Link to another page' });

            act(() => {
                userEvent.click(link);
            });

            expect(screen.getByText('Another page')).toBeInTheDocument();
            const skipLink = screen.getByRole('link', { name: 'Skip to main content' });

            userEvent.tab();
            expect(skipLink).toHaveFocus();
        });

        it('does not reset focus if route has not changed', async () => {
            renderTestApp();

            const linkToTheSamePage = screen.getByRole('link', {
                name: 'Link to something in the same page',
            });

            act(() => {
                userEvent.click(linkToTheSamePage);
            });
            const skipLink = screen.getByRole('link', { name: 'Skip to main content' });

            userEvent.tab();
            expect(skipLink).not.toHaveFocus();
        });
    });
});

const renderTestApp = (initialUrl: string = '/testPage1', isLoggedIn: boolean = false) => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };
    render(
        <SessionProvider sessionOverride={isLoggedIn ? auth : undefined}>
            <MemoryRouter initialEntries={[initialUrl]}>
                <Layout>
                    <Routes>
                        <Route path="/" element={<></>}></Route>
                        <Route
                            path="/testPage1"
                            element={
                                <div>
                                    <h1>Test heading 1</h1>
                                    <h2>Test heading 2</h2>
                                    <p>Some content</p>
                                    <Link to="/withoutSizeOneHeading">Link to another page</Link>
                                    <span id="someElement">Linked element in the same page</span>
                                    <Link to="#someElement">
                                        Link to something in the same page
                                    </Link>
                                </div>
                            }
                        ></Route>
                        <Route
                            path="/withoutSizeOneHeading"
                            element={
                                <div>
                                    <h2>Another page</h2>
                                    <p>Some other content</p>
                                </div>
                            }
                        ></Route>
                    </Routes>
                </Layout>
            </MemoryRouter>
        </SessionProvider>,
    );
};
