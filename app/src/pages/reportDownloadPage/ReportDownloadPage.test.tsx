import { render, waitFor } from '@testing-library/react';
import ReportDownloadPage from './ReportDownloadPage';
import { routes } from '../../types/generic/routes';
import { createMemoryHistory, History } from 'history';
import * as ReactRouter from 'react-router-dom';
import useConfig from '../../helpers/hooks/useConfig';
import { buildConfig } from '../../helpers/test/testBuilders';

const mockedUseNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockedUseNavigate,
    useSearchParams: () => [
        {
            get: jest.fn().mockReturnValue('0'),
        },
    ],
}));
jest.mock('../../types/generic/reports', () => ({
    getReportByType: jest.fn().mockReturnValue({}),
}));
jest.mock('../../helpers/hooks/useConfig');

const mockUseConfig = useConfig as jest.Mock;

let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('ReportDownloadPage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
        mockUseConfig.mockReturnValue(buildConfig());
    });

    it('should redirect to home page if report type is missing', async () => {
        jest.mock('react-router-dom', () => ({
            useSearchParams: () => [],
        }));

        renderPage(history);

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
        });
    });

    it('should redirect to home page if report type does not find a match', async () => {
        jest.mock('../../types/generic/reports', () => ({
            getReportByType: jest.fn().mockReturnValue(null),
        }));

        renderPage(history);

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
        });
    });

    const renderPage = (history: History) => {
        return render(
            <ReactRouter.Router navigator={history} location={history.location}>
                <ReportDownloadPage />
            </ReactRouter.Router>,
        );
    };
});
