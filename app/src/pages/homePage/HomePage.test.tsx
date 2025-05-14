import { render, screen } from '@testing-library/react';
import HomePage from './HomePage';
import useRole from '../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { buildConfig } from '../../helpers/test/testBuilders';
import useConfig from '../../helpers/hooks/useConfig';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockedUseNavigate,
    };
});

vi.mock('../../helpers/hooks/useRole');
vi.mock('../../helpers/hooks/useConfig');
const mockUseRole = useRole as Mock;
const mockUseConfig = useConfig as Mock;

describe('HomePage', () => {
    beforeEach(() => {
        mockUseConfig.mockReturnValue(buildConfig());
    });
    afterEach(() => {
        vi.clearAllMocks();
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
