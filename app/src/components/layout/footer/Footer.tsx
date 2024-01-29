import React from 'react';
import { Footer as NHSFooter } from 'nhsuk-react-components';
import { routes } from '../../../types/generic/routes';

function Footer() {
    return (
        <NHSFooter>
            <NHSFooter.List>
                <NHSFooter.ListItem
                    href={routes.PRIVACY_POLICY}
                    data-testid="privacy-link"
                    rel="opener"
                    target="_blank"
                >
                    Privacy notice
                </NHSFooter.ListItem>
            </NHSFooter.List>
            <NHSFooter.Copyright>&copy; {'Crown copyright'}</NHSFooter.Copyright>
        </NHSFooter>
    );
}

export default Footer;
