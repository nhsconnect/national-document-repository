import { render, screen, waitFor } from '@testing-library/react';
import DocumentsListView from './DocumentsListView';
import { buildDocument, buildTextFile } from '../../../helpers/test/testBuilders';
import { DOCUMENT_UPLOAD_STATE as documentUploadStates } from '../../../types/pages/UploadDocumentsPage/types';
import userEvent from '@testing-library/user-event';
import { act } from 'react-dom/test-utils';

const mockDocuments = [
    buildDocument(buildTextFile('test1'), documentUploadStates.SUCCEEDED),
    buildDocument(buildTextFile('test2'), documentUploadStates.SUCCEEDED),
];

describe('DocumentsListView', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders "Hide files" on page load', () => {
        render(<DocumentsListView documentsList={mockDocuments} ariaLabel={'test'} />);

        expect(screen.getByText('Hide files')).toBeInTheDocument();
        expect(screen.getByText('test1.txt')).toBeInTheDocument();
        expect(screen.getByText('test2.txt')).toBeInTheDocument();

        expect(screen.queryByText('View files')).not.toBeInTheDocument();
    });

    it('renders "View files" when files are not displayed', async () => {
        render(<DocumentsListView documentsList={mockDocuments} ariaLabel={'test'} />);

        act(() => {
            userEvent.click(screen.getByText('Hide files'));
        });

        await waitFor(() => {
            expect(screen.getByText('View files')).toBeInTheDocument();
        });

        expect(screen.queryByText('Hide files')).not.toBeInTheDocument();
        expect(screen.queryByText('test1.txt')).not.toBeVisible();
        expect(screen.queryByText('test2.txt')).not.toBeVisible();
    });
});
