import { render, screen } from '@testing-library/react';
import Layout from './Layout';
import { MemoryRouter as Router } from 'react-router-dom';
import SessionProvider from '../../providers/sessionProvider/SessionProvider';
import userEvent from '@testing-library/user-event';

describe('Layout', () => {
    describe('SkipLink', () => {
        it('renders a skip link element', () => {
            renderLayout();
            expect(screen.getByRole('link', { name: 'Skip to main content' })).toBeInTheDocument();
        });

        it('focus on the first h1 element when triggered', () => {
            renderLayout();

            const skipLink = screen.getByRole('link', { name: 'Skip to main content' });
            const firstH1Heading = screen.getByRole('heading', { name: 'Test heading 1' });

            userEvent.tab();
            expect(skipLink).toHaveFocus();

            userEvent.keyboard('[Enter]');
            expect(firstH1Heading).toHaveFocus();
        });

        it('focus on the main element if there is no h1 heading in the page', () => {
            renderLayoutWithoutH1Heading();

            const skipLink = screen.getByRole('link', { name: 'Skip to main content' });
            const mainContent = screen.getByRole('main');

            userEvent.tab();
            expect(skipLink).toHaveFocus();

            userEvent.keyboard('[Enter]');
            expect(mainContent).toHaveFocus();
        });
    });
});

const renderLayout = () => {
    render(
        <SessionProvider>
            <Router>
                <Layout>
                    <div>
                        <h1>Test heading 1</h1>
                        <h2>Test heading 2</h2>
                        <p>Some content</p>
                    </div>
                </Layout>
            </Router>
        </SessionProvider>,
    );
};

const renderLayoutWithoutH1Heading = () => {
    render(
        <SessionProvider>
            <Router>
                <Layout>
                    <div>
                        <h2>Test heading 2</h2>
                        <p>Some content</p>
                    </div>
                </Layout>
            </Router>
        </SessionProvider>,
    );
};
