import { render, screen, waitFor } from '@testing-library/react';
import UploadDocumentsPage from './UploadDocumentsPage';
import { buildConfig } from '../../helpers/test/testBuilders';
import { UPLOAD_STAGE } from '../../types/pages/UploadDocumentsPage/types';
import { useState } from 'react';
import useConfig from '../../helpers/hooks/useConfig';
import { routes } from '../../types/generic/routes';
import UnauthorisedPage from '../unauthorisedPage/UnauthorisedPage';
import { runAxeTest } from '../../helpers/test/axeTestHelper';

const mockUseState = useState as jest.Mock;
const mockConfigContext = useConfig as jest.Mock;
const mockedUseNavigate = jest.fn();

jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
    useLocation: () => jest.fn(),
}));
jest.mock('react', () => ({
    ...jest.requireActual('react'),
    useState: jest.fn(),
}));
jest.mock('../../components/blocks/_arf/selectStage/SelectStage', () => () => (
    <h1>Mock file input stage</h1>
));
jest.mock('../../components/blocks/_arf/uploadingStage/UploadingStage', () => () => (
    <h1>Mock files are uploading stage</h1>
));
jest.mock('../../components/blocks/_arf/completeStage/CompleteStage', () => () => (
    <h1>Mock complete stage</h1>
));
jest.mock('../../helpers/hooks/useConfig');

describe('UploadDocumentsPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockConfigContext.mockReturnValue(
            buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: true }),
        );
        mockUseState.mockImplementation(() => [UPLOAD_STAGE.Selecting, jest.fn()]);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders initial file input stage', async () => {
            render(<UploadDocumentsPage />);

            expect(
                screen.getByRole('heading', { name: 'Mock file input stage' }),
            ).toBeInTheDocument();
            await waitFor(() => {
                expect(mockedUseNavigate).not.toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });

        it('renders uploading stage when state is set', async () => {
            mockUseState.mockImplementation(() => [UPLOAD_STAGE.Uploading, jest.fn()]);

            render(<UploadDocumentsPage />);

            expect(
                screen.getByRole('heading', { name: 'Mock files are uploading stage' }),
            ).toBeInTheDocument();
            await waitFor(() => {
                expect(mockedUseNavigate).not.toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });

        it('renders upload complete stage when state is set', async () => {
            mockUseState.mockImplementation(() => [UPLOAD_STAGE.Complete, jest.fn()]);

            render(<UploadDocumentsPage />);

            expect(
                screen.getByRole('heading', { name: 'Mock complete stage' }),
            ).toBeInTheDocument();
            await waitFor(() => {
                expect(mockedUseNavigate).not.toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });

        it('pass accessibility checks', async () => {
            render(<UploadDocumentsPage />);
            const results = await runAxeTest(document.body);

            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('redirects to unauthorised page if arf workflow feature toggled off', async () => {
            mockConfigContext.mockReturnValue(
                buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: false }),
            );

            render(<UploadDocumentsPage />);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });
        it('redirects to unauthorised page if upload lambda feature toggled off', async () => {
            mockConfigContext.mockReturnValue(
                buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: false }),
            );

            render(<UploadDocumentsPage />);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });
        it('redirects to unauthorised page if both features toggled off', async () => {
            mockConfigContext.mockReturnValue(
                buildConfig({}, { uploadArfWorkflowEnabled: false, uploadLambdaEnabled: false }),
            );

            render(<UploadDocumentsPage />);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });
    });
});
