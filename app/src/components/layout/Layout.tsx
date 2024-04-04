import React, { MouseEvent, useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import Header from './header/Header';
import PhaseBanner from './phaseBanner/PhaseBanner';
import Footer from './footer/Footer';
import { SkipLink } from 'nhsuk-react-components';
import { useLocation } from 'react-router-dom';
import { focusElement } from '../../helpers/utils/manageFocus';

type Props = {
    children: ReactNode;
};

function Layout({ children }: Props) {
    const layoutRef = useRef<HTMLDivElement | null>(null);
    const mainRef = useRef<HTMLDivElement | null>(null);
    const location = useLocation();

    // re-focus the layout on route change, so that skip link become the next focusable element
    useEffect(() => {
        if (location?.hash) {
            return;
        }

        layoutRef?.current?.focus();
    }, [location]);

    const focusMainContent = (e: MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();

        const firstHeadingElement = document.getElementsByTagName('h1')[0];
        if (firstHeadingElement) {
            focusElement(firstHeadingElement);
        } else if (mainRef?.current) {
            focusElement(mainRef.current);
        }
    };

    return (
        <div ref={layoutRef} tabIndex={-1} id="layout">
            <SkipLink onClick={focusMainContent}>Skip to main content</SkipLink>
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
                    ref={mainRef}
                    role="main"
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
