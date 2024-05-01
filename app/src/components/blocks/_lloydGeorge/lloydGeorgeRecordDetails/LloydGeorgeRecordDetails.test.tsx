import { render, screen } from '@testing-library/react';
import LgRecordDetails, { Props } from './LloydGeorgeRecordDetails';
import { buildLgSearchResult } from '../../../../helpers/test/testBuilders';
import formatFileSize from '../../../../helpers/utils/formatFileSize';

const mockPdf = buildLgSearchResult();

describe('LloydGeorgeRecordDetails', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the record details component', () => {
            renderComponent();

            expect(screen.getByText(`Last updated: ${mockPdf.last_updated}`)).toBeInTheDocument();
            expect(screen.getByText(`${mockPdf.number_of_files} files`)).toBeInTheDocument();
            expect(
                screen.getByText(`File size: ${formatFileSize(mockPdf.total_file_size_in_byte)}`),
            ).toBeInTheDocument();
            expect(screen.getByText('File format: PDF')).toBeInTheDocument();
        });
    });
});

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Props = {
        lastUpdated: mockPdf.last_updated,
        numberOfFiles: mockPdf.number_of_files,
        totalFileSizeInByte: mockPdf.total_file_size_in_byte,
        ...propsOverride,
    };
    return render(<LgRecordDetails {...props} />);
};
