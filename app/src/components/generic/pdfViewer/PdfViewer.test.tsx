import { render, screen } from '@testing-library/react';
import PdfViewer from './PdfViewer';

describe('PdfViewer', () => {
    it('renders an embed element', () => {
        const mockSetCount = jest.fn();
        render(
            <PdfViewer
                fileUrl="https://test"
                searchTerm={''}
                updateSearchResultsCount={mockSetCount}
            />,
        );

        expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
    });
});
