import { render } from '@testing-library/react';
import RecordCard from './RecordCard';

const MockDetails = () => <div>Details</div>;
const mockFullscreenHandler = jest.fn();

describe('RecordCard', () => {
    describe('Rendering', () => {
        it('renders component', () => {
            render(
                <RecordCard
                    detailsElement={<MockDetails />}
                    heading="Jest Record"
                    fullScreenHandler={mockFullscreenHandler}
                    recordUrl={'http://test'}
                />,
            );
        });
    });
});
