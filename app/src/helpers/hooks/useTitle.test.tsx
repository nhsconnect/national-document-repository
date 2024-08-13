import useTitle from './useTitle';
import { render } from '@testing-library/react';

describe('useTitle', () => {
    describe('Set page title', () => {
        it('sets title when string is passes', async () => {
            const title = document.title;
            expect(title).toBe('');

            render(<TestApp />);

            expect(document.title).toBe('test title - Access and store digital patient documents');
        });
    });
});

const TestApp = () => {
    const newPageTitle: string = 'test title';
    useTitle({ pageTitle: newPageTitle });

    return <div></div>;
};
