import { render, screen } from '@testing-library/react';
import Footer from './Footer';
import { routes } from '../../../types/generic/routes';
import { describe, expect, it } from 'vitest';

describe('Footer', () => {
    describe('Rendering', () => {
        it('renders privacy policy link', () => {
            render(<Footer />);
            expect(screen.getByTestId('privacy-link')).toBeInTheDocument();
        });
        it('renders service updates link', () => {
            render(<Footer />);
            expect(screen.getByTestId('service-updates-link')).toBeInTheDocument();
        });
        it('renders help and guidance link', () => {
            render(<Footer />);
            expect(screen.getByTestId('help-and-guidance-link')).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates to privacy policy when link is clicked', () => {
            render(<Footer />);
            expect(screen.getByTestId('privacy-link')).toBeInTheDocument();
            expect(screen.getByTestId('privacy-link')).toHaveAttribute(
                'href',
                routes.PRIVACY_POLICY,
            );
            expect(screen.getByTestId('privacy-link')).toHaveAttribute('rel', 'opener');
            expect(screen.getByTestId('privacy-link')).toHaveAttribute('target', '_blank');
        });
    });
});
