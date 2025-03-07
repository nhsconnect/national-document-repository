import { render, screen } from '@testing-library/react';
import HomePage from './HomePage';
import useRole from '../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { buildConfig } from '../../helpers/test/testBuilders';
import useConfig from '../../helpers/hooks/useConfig';

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
        expect(downloadReportButton).toBeInTheDocument();
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
