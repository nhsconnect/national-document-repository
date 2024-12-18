import { render, screen } from '@testing-library/react';
import LgRecordDetails, { Props } from './LloydGeorgeRecordDetails';
import { buildLgSearchResult } from '../../../../helpers/test/testBuilders';

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

            expect(screen.getByText(`Last updated: ${mockPdf.lastUpdated}`)).toBeInTheDocument();
        });
    });
});

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Props = {
        lastUpdated: mockPdf.lastUpdated,
        ...propsOverride,
    };
    return render(<LgRecordDetails {...props} />);
};
