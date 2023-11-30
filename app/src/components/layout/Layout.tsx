import React from 'react';
import type { ReactNode } from 'react';
import Header from './header/Header';
import { Footer } from 'nhsuk-react-components';
import PhaseBanner from './phaseBanner/testBanner';

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
                <Footer.Copyright>&copy; {'Crown copyright'}</Footer.Copyright>
            </Footer>
        </div>
    );
}

export default Layout;
