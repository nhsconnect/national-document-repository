export function focusElement(element: HTMLElement): void {
    if (document.activeElement === element) {
        return;
    }

    if (!element.hasAttribute('tabIndex')) {
        element.setAttribute('tabIndex', '-1');
        element.addEventListener(
            'blur',
            (e) => {
                e.preventDefault();
                element.removeAttribute('tabIndex');
            },
            { once: true },
        );
    }

    element.focus();
}
