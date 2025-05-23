import { render, screen } from '@testing-library/react';
import WarningText from './WarningText';
import { describe, expect, it } from 'vitest';

describe('Warning text', () => {
    it('displays bold text with a warning icon', () => {
        const mockText = 'Downloading a record will remove it from our storage.';

        render(<WarningText text={mockText} />);

        const warningIcon = screen.getByText('!');
        expect(warningIcon).toBeInTheDocument();

        const textElement = screen.getByText(mockText);
        expect(textElement).toBeInTheDocument();
        expect(textElement.tagName).toBe('STRONG');
    });
});
