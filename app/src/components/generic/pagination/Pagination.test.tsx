import { act, useState } from 'react';
import Pagination, { Props } from './Pagination';
import { render, screen, waitFor } from '@testing-library/react';
import { it, describe } from 'vitest';
import userEvent from '@testing-library/user-event';

describe('Pagination', () => {
    it.each([
        { totalPages: 2, expectedLinkCount: 2 },
        { totalPages: 7, expectedLinkCount: 7 },
        { totalPages: 8, expectedLinkCount: 6 },
        { totalPages: 10, expectedLinkCount: 6 },
    ])("renders expected links when there are '%s' pages", async (theory) => {
        renderApp(theory.totalPages);

        expect(await screen.findAllByTestId(/page-[0-9]+-button/)).toHaveLength(
            theory.expectedLinkCount,
        );

        expect(screen.queryAllByTestId('page-separator')).toHaveLength(
            theory.totalPages > 7 ? 1 : 0,
        );

        expect(await screen.findByTestId('next-page-button')).toBeInTheDocument();
    });

    it('should change current page when clicking next page button', async () => {
        renderApp(2);

        act(() => {
            userEvent.click(screen.getByTestId('next-page-button'));
        });

        await waitFor(async () => {
            expect(await screen.findByTestId('previous-page-button')).toBeInTheDocument();
            expect(screen.queryByTestId('next-page-button')).not.toBeInTheDocument();

            const buttonWrapper = (await screen.findByTestId('page-2-button')).parentElement;
            expect(buttonWrapper).toHaveClass('govuk-pagination__item--current');
        });
    });

    it('should change current page when clicking previous page button', async () => {
        renderApp(2, 1);

        act(() => {
            userEvent.click(screen.getByTestId('previous-page-button'));
        });

        await waitFor(async () => {
            expect(await screen.findByTestId('next-page-button')).toBeInTheDocument();
            expect(screen.queryByTestId('previous-page-button')).not.toBeInTheDocument();

            const buttonWrapper = (await screen.findByTestId('page-1-button')).parentElement;
            expect(buttonWrapper).toHaveClass('govuk-pagination__item--current');
        });
    });

    const TestApp = (props: Partial<Props>) => {
        const [currentPage, setCurrentPage] = useState<number>(props.currentPage!);

        return (
            <Pagination
                currentPage={currentPage}
                setCurrentPage={setCurrentPage}
                totalPages={props.totalPages || 0}
            ></Pagination>
        );
    };

    const renderApp = (totalPages: number, initialPage: number = 0) => {
        return render(<TestApp currentPage={initialPage} totalPages={totalPages}></TestApp>);
    };
});
