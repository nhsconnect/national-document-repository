import { render, screen } from '@testing-library/react';
import RecordCard from './RecordCard';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';

const MockDetails = () => <h1>Mock details render</h1>;
const mockFullscreenHandler = jest.fn();

describe('RecordCard', () => {
    describe('Rendering', () => {
        it('renders component', () => {
            const header = 'Jest Record';
            render(
                <RecordCard
                    downloadStage={DOWNLOAD_STAGE.SUCCEEDED}
                    detailsElement={<MockDetails />}
                    heading={header}
                    fullScreenHandler={mockFullscreenHandler}
                    recordUrl={'http://test'}
                />,
            );
            expect(
                screen.getByRole('heading', { name: 'Mock details render' }),
            ).toBeInTheDocument();
            expect(screen.getByRole('heading', { name: header })).toBeInTheDocument();
            expect(screen.getByText('View record')).toBeInTheDocument();
            expect(screen.getByText('View in full screen')).toBeInTheDocument();
            expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
        });

        it('does not render pdf viewer when download stage not succeeded', () => {
            const header = 'Jest Record';
            render(
                <RecordCard
                    downloadStage={DOWNLOAD_STAGE.NO_RECORDS}
                    detailsElement={<MockDetails />}
                    heading={header}
                    fullScreenHandler={mockFullscreenHandler}
                    recordUrl={'http://test'}
                />,
            );
            expect(
                screen.getByRole('heading', { name: 'Mock details render' }),
            ).toBeInTheDocument();
            expect(screen.getByRole('heading', { name: header })).toBeInTheDocument();
            expect(screen.queryByText('View record')).not.toBeInTheDocument();
            expect(screen.queryByText('View in full screen')).not.toBeInTheDocument();
            expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
        });
    });
});
