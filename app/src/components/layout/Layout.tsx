import React from 'react';
import type { ReactNode } from 'react';
import Header from './header/Header';
import PhaseBanner from './phaseBanner/PhaseBanner';
import Footer from './footer/Footer';

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
            <Footer />
        </div>
    );
}

export default Layout;
