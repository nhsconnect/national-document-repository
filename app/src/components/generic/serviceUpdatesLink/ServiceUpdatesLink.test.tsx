import { render, screen } from '@testing-library/react';
import ServiceUpdatesLink from './ServiceUpdatesLink';

describe('Service updates link', () => {
    it('renders a service updates link that opens in a new tab', () => {
        render(<ServiceUpdatesLink />);

        const serviceUpdatesLink = screen.getByRole('link', {
            name: /Service updates/i,
        });

        expect(serviceUpdatesLink).toHaveAttribute(
            'href',
            'https://digital.nhs.uk/services/access-and-store-digital-patient-documents/service-updates',
        );
        expect(serviceUpdatesLink).toHaveAttribute('target', '_blank');
    });
});
