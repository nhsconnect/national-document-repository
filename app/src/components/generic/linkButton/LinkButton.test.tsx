import { render, screen } from '@testing-library/react';
import LinkButton from './LinkButton';

describe('LinkButton', () => {
    it('renders component', () => {
        const buttonString = 'Test Button';
        render(<LinkButton>{buttonString}</LinkButton>);

        expect(screen.getByRole('button', { name: buttonString })).toBeInTheDocument();
    });
});
