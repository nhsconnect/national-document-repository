import { render, screen, waitFor } from '@testing-library/react';
import UploadDocumentsPage from './UploadDocumentsPage';
import { buildConfig, buildTextFile } from '../../helpers/test/testBuilders';
import { UPLOAD_STAGE } from '../../types/pages/UploadDocumentsPage/types';
// import { useState } from 'react';
import useConfig from '../../helpers/hooks/useConfig';
import { routeChildren, routes } from '../../types/generic/routes';
import UnauthorisedPage from '../unauthorisedPage/UnauthorisedPage';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { createMemoryHistory, History } from 'history';
import * as ReactRouter from 'react-router';
import LloydGeorgeUploadPage from '../lloydGeorgeUploadPage/LloydGeorgeUploadPage';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import usePatient from '../../helpers/hooks/usePatient';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { childRoutes } from '../../router/AppRouter';
import uploadDocuments, { uploadDocumentToS3 } from '../../helpers/requests/uploadDocuments';

// const mockUseState = useState as jest.Mock;
const mockConfigContext = useConfig as jest.Mock;
const mockedUseNavigate = jest.fn();
const mockUploadDocuments = uploadDocuments as jest.Mock;
const mockS3Upload = uploadDocumentToS3 as jest.Mock;

jest.mock('react-router', () => ({
    ...jest.requireActual('react-router'),
    useNavigate: () => mockedUseNavigate,
    // useLocation: () => jest.fn(),
}));
jest.mock('../../helpers/requests/uploadDocuments');
jest.mock('../../helpers/hooks/usePatient');
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useBaseAPIUrl');

// jest.mock('../../components/blocks/_arf/selectStage/SelectStage', () => () => (
//     <h1>Mock file input stage</h1>
// ));
// jest.mock('../../components/blocks/_arf/uploadingStage/UploadingStage', () => () => (
//     <h1>Mock files are uploading stage</h1>
// ));
// jest.mock('../../components/blocks/_arf/completeStage/CompleteStage', () => () => (
//     <h1>Mock complete stage</h1>
// ));
jest.mock('../../helpers/hooks/useConfig');

let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('UploadDocumentsPage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });

        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockConfigContext.mockReturnValue(
            buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: true }),
        );
        // mockUseState.mockImplementation(() => [UPLOAD_STAGE.Selecting, jest.fn()]);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders initial file input stage', async () => {
            renderPage(history);

            expect(screen.getByTestId('arf-upload-select-stage-header')).toBeInTheDocument();
            await waitFor(() => {
                expect(mockedUseNavigate).not.toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });

        it('renders uploading stage when state is set', async () => {
            renderPage(history);
            const arfFile = buildTextFile('arf-test.txt', 100);

            act(() => {
                userEvent.upload(screen.getByTestId(`ARF-input`), [arfFile]);
                userEvent.click(screen.getByTestId('arf-upload-submit-btn'));
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routeChildren.ARF_UPLOAD_UPLOADING);
            });
        });

        it('pass accessibility checks', async () => {
            renderPage(history);
            const results = await runAxeTest(document.body);

            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('redirects to unauthorised page if arf workflow feature toggled off', async () => {
            mockConfigContext.mockReturnValue(
                buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: false }),
            );

            renderPage(history);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });
        it('redirects to unauthorised page if upload lambda feature toggled off', async () => {
            mockConfigContext.mockReturnValue(
                buildConfig({}, { uploadArfWorkflowEnabled: true, uploadLambdaEnabled: false }),
            );

            renderPage(history);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });
        it('redirects to unauthorised page if both features toggled off', async () => {
            mockConfigContext.mockReturnValue(
                buildConfig({}, { uploadArfWorkflowEnabled: false, uploadLambdaEnabled: false }),
            );

            renderPage(history);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
            });
        });
    });
});

const renderPage = (history: History) => {
    return render(
        <ReactRouter.Router navigator={history} location={history.location}>
            <UploadDocumentsPage />
        </ReactRouter.Router>,
    );
};
