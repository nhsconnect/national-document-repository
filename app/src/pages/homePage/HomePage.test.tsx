import { render, screen, waitFor } from '@testing-library/react';
import HomePage from './HomePage';
import { routes } from '../../types/generic/routes';
import useRole from '../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { REPORT_TYPE } from '../../types/generic/reports';
import { buildConfig } from '../../helpers/test/testBuilders';
import useConfig from '../../helpers/hooks/useConfig';
import userEvent from '@testing-library/user-event';
import { act } from 'react-dom/test-utils';

const mockedUseNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

jest.mock('../../helpers/hooks/useRole');
jest.mock('../../helpers/hooks/useConfig');
const mockUseRole = useRole as jest.Mock;
const mockUseConfig = useConfig as jest.Mock;

describe('HomePage', () => {
    beforeEach(() => {
        mockUseConfig.mockReturnValue(buildConfig());
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    const gpRoles = [REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL];

    const validateHomePageRendered = () => {
        render(<HomePage />);

        const searchPatientButton = screen.getByTestId('search-patient-btn') as HTMLAnchorElement;
        const downloadReportButton = screen.getByTestId('download-report-btn') as HTMLAnchorElement;
        expect(searchPatientButton).toBeInTheDocument();
        expect(searchPatientButton.href).toBe(`http://localhost${routes.SEARCH_PATIENT}`);
        expect(downloadReportButton).toBeInTheDocument();
        expect(downloadReportButton.href).toBe(
            `http://localhost${routes.REPORT_DOWNLOAD}?reportType=${REPORT_TYPE.ODS_PATIENT_SUMMARY}`,
        );
    };

    describe('Rendering for GP roles', () => {
        it.each(gpRoles)(
            '[%s] render home page with patient search and download report',
            async (role) => {
                mockUseRole.mockReturnValue(role);

                validateHomePageRendered();
            },
        );
    });

    describe('PCSE Rendering', () => {
        it('should render home page with patient search and download report', async () => {
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);

            validateHomePageRendered();
        });
    });
});
