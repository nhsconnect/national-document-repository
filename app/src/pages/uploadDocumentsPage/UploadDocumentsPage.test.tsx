import { render, screen, waitFor } from '@testing-library/react';
import UploadDocumentsPage from './UploadDocumentsPage';
import { buildConfig, buildTextFile } from '../../helpers/test/testBuilders';
import useConfig from '../../helpers/hooks/useConfig';
import { routeChildren, routes } from '../../types/generic/routes';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { createMemoryHistory, History } from 'history';
import * as ReactRouter from 'react-router';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';

const mockConfigContext = useConfig as jest.Mock;
const mockedUseNavigate = jest.fn();

jest.mock('react-router', () => ({
    ...jest.requireActual('react-router'),
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('../../helpers/requests/uploadDocuments');
jest.mock('../../helpers/hooks/usePatient');
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useBaseAPIUrl');

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
