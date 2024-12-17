import React from 'react';
import { Footer as NHSFooter } from 'nhsuk-react-components';
import { routes } from '../../../types/generic/routes';
import ServiceUpdatesLink from '../../generic/serviceUpdatesLink/ServiceUpdatesLink';

function Footer() {
    return (
        <NHSFooter>
            <NHSFooter.List>
                <NHSFooter.ListItem
                    href={routes.PRIVACY_POLICY}
                    data-testid="privacy-link"
                    rel="opener"
                    target="_blank"
                    aria-label="(Privacy notice - this link will open in a new tab)"
                >
                    Privacy notice
                </NHSFooter.ListItem>
                <ServiceUpdatesLink />
            </NHSFooter.List>
            <NHSFooter.Copyright>&copy; {'Crown copyright'}</NHSFooter.Copyright>
        </NHSFooter>
    );
}

export default Footer;
