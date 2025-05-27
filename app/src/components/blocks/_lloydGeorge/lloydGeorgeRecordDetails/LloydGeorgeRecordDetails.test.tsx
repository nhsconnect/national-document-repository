import { render, screen } from '@testing-library/react';
import LgRecordDetails, { Props } from './LloydGeorgeRecordDetails';
import { buildLgSearchResult } from '../../../../helpers/test/testBuilders';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

const mockPdf = buildLgSearchResult();

describe('LloydGeorgeRecordDetails', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });

    afterEach(() => {
        vi.clearAllMocks();
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
