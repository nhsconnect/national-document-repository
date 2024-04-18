import pageTitle from './PageTitle';
import { render } from '@testing-library/react';

describe('PageTitle', () => {
    describe('Set page title', () => {
        it('sets title when string is passes', async () => {
            const title = document.title;
            expect(title).toBe('');

            render(<TestApp />);

            expect(document.title).toBe('test title - Digital Lloyd George records');
        });
    });
});

const TestApp = () => {
    const newPageTitle: string = 'test title';
    pageTitle({ pageTitle: newPageTitle });

    return <div></div>;
};
