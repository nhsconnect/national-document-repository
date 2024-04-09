import { render, screen } from '@testing-library/react';
import { focusElement, focusLayoutDiv } from './manageFocus';
import userEvent from '@testing-library/user-event';

describe('focusElement', () => {
    it('set focus to the given element', () => {
        renderTestApp();

        const h1 = screen.getByRole('heading', { name: 'Test heading' });

        focusElement(h1);

        expect(h1).toHaveFocus();
        expect(h1).toHaveAttribute('tabIndex', '-1');

        userEvent.tab();
        expect(h1).not.toHaveFocus();
        expect(h1).not.toHaveAttribute('tabIndex');
    });

    it('does not change the existing tab index of element', () => {
        renderTestApp();

        const spanWithTabIndexZero = screen.getByText('element that already has tab index');

        focusElement(spanWithTabIndexZero);

        expect(spanWithTabIndexZero).toHaveFocus();
        expect(spanWithTabIndexZero).toHaveAttribute('tabindex', '0');
    });
});

describe('focusLayoutDiv', () => {
    it('set focus to the layout div', () => {
        renderTestApp();

        const layoutDiv = screen.getByTestId('layoutDiv');

        focusLayoutDiv();

        expect(layoutDiv).toHaveFocus();
    });
});

const renderTestApp = () => {
    render(
        <div id="layout" data-testid="layoutDiv">
            <h1>Test heading</h1>
            <span tabIndex={0}>element that already has tab index</span>
            <input type="text"></input>
        </div>,
    );
};
