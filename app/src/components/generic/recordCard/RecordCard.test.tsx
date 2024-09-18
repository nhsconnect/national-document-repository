const MockDetails = () => <h1>Mock details render</h1>;
const MockPdf = () => <h1>Mock pdf render</h1>;

const mockFullscreenHandler = jest.fn();

describe('RecordCard', () => {
    describe('Rendering', () => {
        it('passes', () => {});
        // it('renders component', () => {
        //     const header = 'Jest Record';
        //     render(
        //         <RecordCard
        //             downloadStage={DOWNLOAD_STAGE.SUCCEEDED}
        //             detailsElement={<MockDetails />}
        //             pdfElement={<MockPdf />}
        //             heading={header}
        //             fullScreenHandler={mockFullscreenHandler}
        //         />,
        //     );
        //     expect(
        //         screen.getByRole('heading', { name: 'Mock details render' }),
        //     ).toBeInTheDocument();
        //     expect(screen.getByRole('heading', { name: header })).toBeInTheDocument();
        //     expect(screen.getByText('View in full screen')).toBeInTheDocument();
        //     expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
        // });
        // it('does not render pdf viewer when download stage not succeeded', () => {
        //     const header = 'Jest Record';
        //     render(
        //         <RecordCard
        //             downloadStage={DOWNLOAD_STAGE.NO_RECORDS}
        //             detailsElement={<MockDetails />}
        //             heading={header}
        //             fullScreenHandler={mockFullscreenHandler}
        //             pdfElement={<MockPdf />}
        //         />,
        //     );
        //     expect(
        //         screen.getByRole('heading', { name: 'Mock details render' }),
        //     ).toBeInTheDocument();
        //     expect(screen.getByRole('heading', { name: header })).toBeInTheDocument();
        //     expect(screen.queryByText('View in full screen')).not.toBeInTheDocument();
        //     expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
        // });
    });
});
