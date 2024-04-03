import React, { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import Header from './header/Header';
import PhaseBanner from './phaseBanner/PhaseBanner';
import Footer from './footer/Footer';
import { SkipLink } from 'nhsuk-react-components';
import { useLocation } from 'react-router-dom';

type Props = {
    children: ReactNode;
};

function Layout({ children }: Props) {
    const layoutRef = useRef<HTMLDivElement | null>(null);
    const location = useLocation();

    // focus the layout div on every route change to ensure user get to skiplink when they press tab
    useEffect(() => {
        if (location?.hash) {
            return;
        }
        if (layoutRef) {
            layoutRef.current?.focus();
        }
    }, [location]);

    return (
        <div ref={layoutRef} tabIndex={-1}>
            <SkipLink>Skip to main content</SkipLink>
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
                <main
                    className="nhsuk-main-wrapper app-homepage"
                    id="maincontent"
                    role="main"
                    tabIndex={-1}
                >
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
