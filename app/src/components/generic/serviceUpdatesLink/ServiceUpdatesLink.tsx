import { Footer as NHSFooter } from 'nhsuk-react-components';

const ServiceUpdatesLink = () => {
    return (
        <NHSFooter.ListItem
            href="https://digital.nhs.uk/services/access-and-store-digital-patient-documents/service-updates"
            data-testid="service-updates-link"
            rel="noopener"
            target="_blank"
            aria-label="Service updates - Opens in a new tab"
        >
            Service updates
        </NHSFooter.ListItem>
    );
};

export default ServiceUpdatesLink;
