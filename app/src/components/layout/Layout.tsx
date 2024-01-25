import React from 'react';
import type { ReactNode } from 'react';
import Header from './header/Header';
import { Footer } from 'nhsuk-react-components';
import PhaseBanner from './phaseBanner/PhaseBanner';
import { routes } from '../../types/generic/routes';
import { Link } from 'react-router-dom';

type Props = {
    children: ReactNode;
};

function Layout({ children }: Props) {
    return (
        <div>
            <Header />
            <PhaseBanner />
            <div
                className="nhsuk-width-container"
                style={{
                    margin: `0 auto`,
                    maxWidth: 960,
                    padding: `0 1.0875rem 1.45rem`,
                    minHeight: '75vh',
                }}
            >
                <main className="nhsuk-main-wrapper app-homepage" id="maincontent" role="main">
                    <section className="app-homepage-content">
                        <div>{children}</div>
                    </section>
                </main>
            </div>
            <Footer>
                <Footer.List>
                    <Footer.ListItem>
                        <Link to={routes.PRIVACY_POLICY}>Privacy notice</Link>
                    </Footer.ListItem>
                </Footer.List>
                <Footer.Copyright>&copy; {'Crown copyright'}</Footer.Copyright>
            </Footer>
        </div>
    );
}

export default Layout;
