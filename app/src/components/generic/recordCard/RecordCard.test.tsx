import { render, screen } from '@testing-library/react';
import RecordCard from './RecordCard';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import {REPOSITORY_ROLE} from "../../../types/generic/authRole";
import useRole from '../../../helpers/hooks/useRole';

jest.mock('../../../helpers/hooks/useRole');
const MockDetails = () => <h1>Mock details render</h1>;
const mockFullscreenHandler = jest.fn();
const mockUseRole = useRole as jest.Mock;

describe('RecordCard', () => {
    describe('Rendering for GP_ADMIN role', () => {
        it('renders component', () => {
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
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
            expect(screen.getByText('View in full screen')).toBeInTheDocument();
            expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
        });

        it('does not render pdf viewer when download stage not succeeded', () => {
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
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
            expect(screen.queryByText('View in full screen')).not.toBeInTheDocument();
            expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
        });
    });
    describe('Rendering for GP_CLINICAL role', () => {
        it('renders component', () => {
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
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
            expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
        });

        it('does not render pdf viewer when download stage not succeeded', () => {
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
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
            expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
        });
    })
});
