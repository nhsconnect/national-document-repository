import { act, render, screen } from '@testing-library/react';
import Layout from './Layout';
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom';
import SessionProvider from '../../providers/sessionProvider/SessionProvider';
import userEvent from '@testing-library/user-event';

describe('Layout', () => {
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

        it('does not misfire if route was not changed', async () => {
            renderTestApp();

            const linkToTheSamePage = screen.getByRole('link', {
                name: 'Link to something in the same page',
            });

            userEvent.click(linkToTheSamePage);
            const skipLink = screen.getByRole('link', { name: 'Skip to main content' });

            userEvent.tab();
            expect(skipLink).not.toHaveFocus();
        });
    });
});

const renderTestApp = (initialUrl: string = '/testPage1') => {
    render(
        <SessionProvider>
            <MemoryRouter initialEntries={[initialUrl]}>
                <Layout>
                    <Routes>
                        <Route
                            path="/testPage1"
                            element={
                                <div>
                                    <h1>Test heading 1</h1>
                                    <h2>Test heading 2</h2>
                                    <p>Some content</p>
                                    <Link to={'/withoutSizeOneHeading'}>Link to another page</Link>
                                    <span id="someElement">Linked element in the same page</span>
                                    <a href="#someElement">Link to something in the same page</a>
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
