import React from 'react';
import { Footer as NHSFooter } from 'nhsuk-react-components';
import { routes } from '../../../types/generic/routes';

const serviceUpdatesLink =
    'https://digital.nhs.uk/services/access-and-store-digital-patient-documents/service-updates';

function Footer() {
    return (
        <NHSFooter>
            <NHSFooter.List>
                <NHSFooter.ListItem
                    href={routes.PRIVACY_POLICY}
                    data-testid="privacy-link"
                    rel="opener"
                    target="_blank"
                    aria-label="Privacy notice - Opens in a new tab"
                >
                    Privacy notice
                </NHSFooter.ListItem>
                <NHSFooter.ListItem
                    href={serviceUpdatesLink}
                    data-testid="service-updates-link"
                    rel="noopener"
                    target="_blank"
                    aria-label="Service updates - Opens in a new tab"
                >
                    Service updates
                </NHSFooter.ListItem>
            </NHSFooter.List>
            {/* TODO - PRMP-1348: Remove hardcoded styling below if no longer required */}
            <NHSFooter.Copyright style={{ color: '#231f20' }}>
                &copy; {'NHS England'}
            </NHSFooter.Copyright>
        </NHSFooter>
    );
}

export default Footer;
