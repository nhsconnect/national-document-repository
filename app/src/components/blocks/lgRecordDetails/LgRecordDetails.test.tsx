import { render, screen, waitFor } from '@testing-library/react';
import LgRecordDetails, { Props } from './LgRecordDetails';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { buildLgSearchResult } from '../../../helpers/test/testBuilders';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
const mockPdf = buildLgSearchResult();

describe('LgRecordDetails', () => {
    const actionLinkStrings = [
        { label: 'See all files', expectedStage: LG_RECORD_STAGE.SEE_ALL },
        { label: 'Download all files', expectedStage: LG_RECORD_STAGE.DOWNLOAD_ALL },
        { label: 'Delete a selection of files', expectedStage: LG_RECORD_STAGE.DELETE_ANY },
        { label: 'Delete file', expectedStage: LG_RECORD_STAGE.DELETE_ONE },
    ];

    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
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
        actionLinkStrings.forEach((action) => {
            expect(screen.queryByText(action.label)).not.toBeInTheDocument();
        });

        userEvent.click(screen.getByTestId('actions-menu'));
        await waitFor(async () => {
            actionLinkStrings.forEach((action) => {
                expect(screen.getByText(action.label)).toBeInTheDocument();
            });
        });
    });

    it.each(actionLinkStrings)(
        "navigates to a new stage when action '%s' is clicked",
        async (action) => {
            renderComponent();

            expect(screen.getByText(`Select an action...`)).toBeInTheDocument();
            expect(screen.getByTestId('actions-menu')).toBeInTheDocument();

            expect(screen.queryByText(action.label)).not.toBeInTheDocument();
            userEvent.click(screen.getByTestId('actions-menu'));
            await waitFor(async () => {
                expect(screen.getByText(action.label)).toBeInTheDocument();
            });

            userEvent.click(screen.getByText(action.label));
            await waitFor(async () => {
                expect(screen.getByTestId(action.expectedStage)).toBeInTheDocument();
            });
        },
    );
});

const TestApp = (props: Omit<Props, 'setStage' | 'stage'>) => {
    const [stage, setStage] = useState(LG_RECORD_STAGE.RECORD);
    const history = createMemoryHistory({
        initialEntries: ['/', '/example'],
        initialIndex: 1,
    });
    return (
        <ReactRouter.Router navigator={history} location={'/example'}>
            <LgRecordDetails {...props} stage={stage} setStage={setStage} />;
        </ReactRouter.Router>
    );
};

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage' | 'stage'> = {
        lastUpdated: mockPdf.last_updated,
        numberOfFiles: mockPdf.number_of_files,
        totalFileSizeInByte: mockPdf.total_file_size_in_byte,

        ...propsOverride,
    };
    return render(<TestApp {...props} />);
};
