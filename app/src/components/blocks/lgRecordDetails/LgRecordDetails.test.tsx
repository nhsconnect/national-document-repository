import { render, screen, waitFor } from '@testing-library/react';
import LgRecordDetails, { Props } from './LgRecordDetails';
import { useState } from 'react';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { buildLgSearchResult } from '../../../helpers/test/testBuilders';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import userEvent from '@testing-library/user-event';
const mockPdf = buildLgSearchResult();

describe('LgRecordDetails', () => {
    const [, setStage] = useState(LG_RECORD_STAGE.RECORD);

    const actionLinkStrings = [
        'See all files',
        'Download all files',
        'Delete a selection of files',
        'Delete file',
    ];

    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
        setStage(LG_RECORD_STAGE.RECORD);
    });

    it('renders the record details component', () => {
        renderComponent();

        expect(screen.getByText(`Last updated: ${mockPdf.last_updated}`)).toBeInTheDocument();
        expect(screen.getByText(`${mockPdf.number_of_files} files`)).toBeInTheDocument();
        expect(
            screen.getByText(`File size: ${formatFileSize(mockPdf.total_file_size_in_byte)}`),
        ).toBeInTheDocument();
        expect(screen.getByText('File format: PDF')).toBeInTheDocument();
    });

    it('renders record details actions menu', async () => {
        renderComponent();

        expect(screen.getByText(`Select an action...`)).toBeInTheDocument();
        expect(screen.getByTestId('actions-menu')).toBeInTheDocument();
        actionLinkStrings.forEach((label) => {
            expect(screen.queryByText(label)).not.toBeInTheDocument();
        });

        userEvent.click(screen.getByTestId('actions-menu'));
        await waitFor(async () => {
            actionLinkStrings.forEach((label) => {
                expect(screen.getByText(label)).toBeInTheDocument();
            });
        });
    });

    const TestApp = (props: Omit<Props, 'setStage'>) => {
        const history = createMemoryHistory({
            initialEntries: ['/', '/example'],
            initialIndex: 1,
        });

        return (
            <ReactRouter.Router navigator={history} location={'/example'}>
                <LgRecordDetails {...props} setStage={setStage} />;
            </ReactRouter.Router>
        );
    };

    const renderComponent = (propsOverride?: Partial<Props>) => {
        const props: Omit<Props, 'setStage'> = {
            lastUpdated: mockPdf.last_updated,
            numberOfFiles: mockPdf.number_of_files,
            totalFileSizeInByte: mockPdf.total_file_size_in_byte,

            ...propsOverride,
        };
        render(<TestApp {...props} />);
    };
});
