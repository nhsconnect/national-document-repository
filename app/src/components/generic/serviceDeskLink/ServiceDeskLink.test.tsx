import { render, screen } from '@testing-library/react';
import ServiceDeskLink from './ServiceDeskLink';

describe('Service desk link', () => {
    it('renders a service desk link that opens in a new tab', () => {
        render(<ServiceDeskLink />);

        const nationalServiceDeskLink = screen.getByRole('link', {
            name: /NHS National Service Desk/i,
        });

        expect(nationalServiceDeskLink).toHaveAttribute(
            'href',
            'https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks',
        );
        expect(nationalServiceDeskLink).toHaveAttribute('target', '_blank');
    });
});
