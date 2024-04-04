import React, { MouseEvent, useEffect, useRef } from 'react';
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
    const mainRef = useRef<HTMLDivElement | null>(null);
    const location = useLocation();

    useEffect(() => {
        if (location?.hash) {
            return;
        }
        layoutRef?.current?.focus();
    }, [location]);

    const focusMain = (e: MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        mainRef?.current?.focus();
    };

    return (
        <div ref={layoutRef} tabIndex={-1}>
            <SkipLink onClick={focusMain}>Skip to main content</SkipLink>
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
                    ref={mainRef}
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
