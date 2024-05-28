import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UploadSummary, { Props } from './UploadSummary';
import {
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { formatFileSize as formatSize } from '../../../../helpers/utils/formatFileSize';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import {
    buildDocument,
    buildPatientDetails,
    buildTextFile,
} from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';

jest.mock('../../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as jest.Mock;
const mockPatient = buildPatientDetails();

describe('UploadSummary', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page', () => {
        renderUploadSummary({ documents: [] });

        expect(screen.getByRole('heading', { name: 'Upload Summary' })).toBeInTheDocument();
        expect(
            screen.getByRole('heading', {
                name: /All documents have been successfully uploaded on/,
            }),
        ).toBeInTheDocument();
        expect(screen.getByText('NHS number')).toBeInTheDocument();
        expect(screen.getByText('Surname')).toBeInTheDocument();
        expect(screen.getByText('First name')).toBeInTheDocument();
        expect(screen.getByText('Date of birth')).toBeInTheDocument();
        expect(screen.getByText('Postcode')).toBeInTheDocument();
        expect(screen.getByText('Before you close this page')).toBeInTheDocument();
        expect(
            screen.queryByText('Some of your documents failed to upload'),
        ).not.toBeInTheDocument();
        expect(screen.queryByText('View successfully uploaded documents')).not.toBeInTheDocument();
    });

    it('displays successfully uploaded docs and callout message', () => {
        const files = [buildTextFile('one', 100), buildTextFile('two', 101)];
        const documents = files.map((file) => buildDocument(file, documentUploadStates.SUCCEEDED));

        renderUploadSummary({ documents });

        expect(
            screen.getByText(/All documents have been successfully uploaded on/),
        ).toBeInTheDocument();
        expect(screen.getByText('View successfully uploaded documents')).toBeInTheDocument();
        const uploadedDocsTable = screen.getByRole('table', {
            name: 'Successfully uploaded documents',
        });
        files.forEach(({ name, size }) => {
            expect(within(uploadedDocsTable).getByText(name)).toBeInTheDocument();
            expect(within(uploadedDocsTable).getByText(formatSize(size))).toBeInTheDocument();
        });
        expect(screen.getByText('Before you close this page')).toBeInTheDocument();
    });

    it('displays a collapsible list of successfully uploaded docs', () => {
        const files = [buildTextFile('test1'), buildTextFile('test2')];
        const documents = files.map((file) => buildDocument(file, documentUploadStates.SUCCEEDED));

        renderUploadSummary({ documents });

        expect(
            screen.queryByRole('table', { name: 'Successfully uploaded documents' }),
        ).not.toBeVisible();

        userEvent.click(screen.getByText('View successfully uploaded documents'));

        expect(
            screen.getByRole('table', { name: 'Successfully uploaded documents' }),
        ).toBeVisible();

        userEvent.click(screen.getByText('View successfully uploaded documents'));

        expect(
            screen.queryByRole('table', { name: 'Successfully uploaded documents' }),
        ).not.toBeVisible();
    });

    it('does not include docs that failed to upload in the successfully uploaded docs list', () => {
        const uploadedFileName = 'one';
        const failedToUploadFileName = 'two';
        const documents = [
            buildDocument(buildTextFile(uploadedFileName, 100), documentUploadStates.SUCCEEDED),
            buildDocument(buildTextFile(failedToUploadFileName, 101), documentUploadStates.FAILED),
        ];

        renderUploadSummary({ documents });

        expect(
            screen.queryByRole('heading', {
                name: /All documents have been successfully uploaded on/,
            }),
        ).not.toBeInTheDocument();
        const uploadedDocsTable = screen.getByRole('table', {
            name: 'Successfully uploaded documents',
        });
        expect(within(uploadedDocsTable).getByText(`${uploadedFileName}.txt`)).toBeInTheDocument();
        expect(
            within(uploadedDocsTable).queryByText(`${failedToUploadFileName}.txt`),
        ).not.toBeInTheDocument();
    });

    it('does not display the successfully uploads docs list when all of the docs failed to upload', () => {
        const documents = [buildDocument(buildTextFile('test1'), documentUploadStates.FAILED)];

        renderUploadSummary({ documents });

        expect(
            screen.queryByRole('heading', {
                name: /All documents have been successfully uploaded on/,
            }),
        ).not.toBeInTheDocument();
        expect(screen.queryByText('View succe0ssfully uploaded documents')).not.toBeInTheDocument();
    });

    it('displays message and does not display an alert if all the docs were uploaded successfully', () => {
        const files = [buildTextFile('one', 100)];
        const documents = [buildDocument(files[0], documentUploadStates.SUCCEEDED)];

        renderUploadSummary({ documents });

        expect(
            screen.getByRole('heading', {
                name:
                    'All documents have been successfully uploaded on ' +
                    getFormattedDate(new Date()),
            }),
        ).toBeInTheDocument();
        expect(
            screen.queryByRole('alert', {
                name: 'Some of your documents failed to upload',
            }),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByText(`${documents.length} of ${files.length} files failed to upload`),
        ).not.toBeInTheDocument();
    });

    it('displays an alert if some of the docs failed to upload', () => {
        const documents = [
            buildDocument(buildTextFile('test1'), documentUploadStates.SUCCEEDED),
            buildDocument(buildTextFile('test2'), documentUploadStates.FAILED),
        ];

        renderUploadSummary({ documents });

        expect(screen.getByRole('alert', { name: 'There is a problem' })).toBeInTheDocument();
        expect(
            screen.getByText(
                'Some documents failed to upload. You can try to upload the documents again if you wish, or they must be printed and sent via PCSE',
            ),
        ).toBeInTheDocument();
        expect(screen.getAllByText('Documents that have failed to upload')).toHaveLength(2);
        expect(
            screen.getByRole('link', { name: 'Documents that have failed to upload' }),
        ).toHaveAttribute('href', '#failed-uploads');
    });

    it('displays each doc that failed to upload in a table', () => {
        const files = [buildTextFile('one', 100), buildTextFile('two', 101)];
        const documents = files.map((file) => buildDocument(file, documentUploadStates.FAILED));

        renderUploadSummary({ documents });

        const failedToUploadDocsTable = screen.getByRole('table', {
            name: /failed to upload/,
        });
        files.forEach(({ name, size }) => {
            expect(within(failedToUploadDocsTable).getByText(name)).toBeInTheDocument();
            expect(within(failedToUploadDocsTable).getByText(formatSize(size))).toBeInTheDocument();
        });
    });

    it('displays number of failed uploads and total uploads when there is at least 1 failed upload', () => {
        const files = [buildTextFile('one', 100), buildTextFile('two', 101)];
        const documents: Array<UploadDocument> = files.map((file) =>
            buildDocument(file, documentUploadStates.FAILED),
        );

        renderUploadSummary({ documents });

        expect(
            screen.getByText(`${documents.length} of ${files.length} files failed to upload`),
        ).toBeInTheDocument();
    });

    describe('Accessibility', () => {
        it('pass accessibility checks when upload result are all successful', async () => {
            const files = [buildTextFile('one', 100), buildTextFile('two', 101)];
            const documents = files.map((file) =>
                buildDocument(file, documentUploadStates.SUCCEEDED),
            );
            renderUploadSummary({ documents });

            await screen.findByText(/All documents have been successfully uploaded/);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when result contain both successful and unsuccessful uploads', async () => {
            const files = [buildTextFile('one', 100), buildTextFile('two', 101)];
            const documents = [
                buildDocument(files[0], documentUploadStates.FAILED),
                buildDocument(files[1], documentUploadStates.SUCCEEDED),
            ];
            renderUploadSummary({ documents });

            await screen.findByText(/files failed to upload/);
            await screen.findByText('View successfully uploaded documents');

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });
});

const renderUploadSummary = (propsOverride: Partial<Props>) => {
    const props: Props = {
        documents: [],
        ...propsOverride,
    };

    render(<UploadSummary {...props} />);
};
