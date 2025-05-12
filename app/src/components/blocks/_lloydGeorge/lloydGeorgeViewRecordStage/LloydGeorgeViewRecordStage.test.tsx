import { LinkProps } from 'react-router-dom';
import usePatient from '../../../../helpers/hooks/usePatient';
import {
    buildConfig,
    buildLgSearchResult,
    buildPatientDetails,
} from '../../../../helpers/test/testBuilders';
import useRole from '../../../../helpers/hooks/useRole';
import useConfig from '../../../../helpers/hooks/useConfig';
import { act, render, screen, waitFor } from '@testing-library/react';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import userEvent from '@testing-library/user-event';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import LloydGeorgeViewRecordStage, { Props } from './LloydGeorgeViewRecordStage';
import { createMemoryHistory } from 'history';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import * as ReactRouter from 'react-router-dom';
import SessionProvider from '../../../../providers/sessionProvider/SessionProvider';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

const mockPdf = buildLgSearchResult();
const mockPatientDetails = buildPatientDetails();
vi.mock('../../../../helpers/hooks/useRole');
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('../../../../helpers/hooks/useConfig');
vi.mock('../../../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');

vi.mock('react-router-dom', async () => ({
    ...(await vi.importActual('react-router-dom')),
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

const mockedUsePatient = usePatient as Mock;
const mockNavigate = vi.fn();
const mockedUseRole = useRole as Mock;
const mockSetStage = vi.fn();
const mockUseConfig = useConfig as Mock;

describe('LloydGeorgeViewRecordStage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatientDetails);
        mockUseConfig.mockReturnValue(buildConfig());
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders an lg record', async () => {
        renderComponent();

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });
        expect(screen.getByText('View in full screen')).toBeInTheDocument();
        expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        expect(screen.getByText(`Last updated: ${mockPdf.lastUpdated}`)).toBeInTheDocument();

        expect(
            screen.queryByText(
                'This patient does not have a Lloyd George record stored in this service.',
            ),
        ).not.toBeInTheDocument();
    });

    const inProgressStages = [
        DOWNLOAD_STAGE.INITIAL,
        DOWNLOAD_STAGE.PENDING,
        DOWNLOAD_STAGE.REFRESH,
    ];

    it.each(inProgressStages)(
        'renders a loading screen if downloading of stitched LG is in progress. Stage name: %s',
        async (stage) => {
            renderComponent({
                downloadStage: stage,
                cloudFrontUrl: '',
            });

            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
        },
    );

    it('renders no docs available text if there is no LG record', async () => {
        renderComponent({
            downloadStage: DOWNLOAD_STAGE.NO_RECORDS,
        });

        await waitFor(async () => {
            expect(
                screen.getByText(
                    /This patient does not have a Lloyd George record stored in this service/i,
                ),
            ).toBeInTheDocument();
        });
    });

    it("renders 'full screen' mode correctly", async () => {
        const patientName = `${mockPatientDetails.givenName}, ${mockPatientDetails.familyName}`;
        const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));

        renderComponent();

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });

        act(() => {
            userEvent.click(screen.getByText('View in full screen'));
        });
        await waitFor(() => {
            expect(screen.queryByText('View in full screen')).not.toBeInTheDocument();
        });
        expect(screen.getByText('Exit full screen')).toBeInTheDocument();
        expect(screen.getByText(patientName)).toBeInTheDocument();
        expect(screen.getByText(`Date of birth: ${dob}`)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
    });

    it("returns to previous view when 'Go back' link clicked during full screen", async () => {
        renderComponent();
        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });

        act(() => {
            userEvent.click(screen.getByText('View in full screen'));
        });
        await waitFor(() => {
            expect(screen.queryByText('View in full screen')).not.toBeInTheDocument();
        });

        act(() => {
            userEvent.click(screen.getByText('Exit full screen'));
        });

        await waitFor(() => {
            expect(screen.getByText('View in full screen')).toBeInTheDocument();
        });
    });

    it('does not render warning callout or button when user is GP admin', async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

        renderComponent();

        expect(screen.queryByText('Before downloading')).not.toBeInTheDocument();
        expect(
            screen.queryByRole('button', { name: 'Download and remove files' }),
        ).not.toBeInTheDocument();
    });

    it('does not render warning callout or button when user is GP clinical', async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);

        renderComponent();

        expect(screen.queryByText('Before downloading')).not.toBeInTheDocument();
        expect(
            screen.queryByRole('button', { name: 'Download and remove files' }),
        ).not.toBeInTheDocument();
    });

    describe.skip('Accessibility', () => {
        it('pass accessibility checks when no LG record are displayed', async () => {
            renderComponent({
                downloadStage: DOWNLOAD_STAGE.NO_RECORDS,
            });

            expect(
                await screen.findByText(
                    /This patient does not have a Lloyd George record stored in this service/,
                ),
            ).toBeInTheDocument();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when displaying LG record', async () => {
            renderComponent();

            expect(await screen.findByTitle('Embedded PDF')).toBeInTheDocument();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks in full screen mode', async () => {
            renderComponent();
            const fullScreenButton = await screen.findByRole('button', {
                name: 'View in full screen',
            });
            act(() => {
                userEvent.click(fullScreenButton);
            });
            expect(screen.getByText('Exit full screen')).toBeInTheDocument();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Go back link', () => {
        it('should navigate to the deceased access audit screen for a deceased patient as a GP User', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            mockedUsePatient.mockReturnValue(buildPatientDetails({ deceased: true }));

            renderComponent();

            act(() => {
                userEvent.click(screen.getByTestId('go-back-button'));
            });

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith(
                    routeChildren.PATIENT_ACCESS_AUDIT_DECEASED,
                );
            });
        });

        it('should navigate to the verify patient screen for a deceased patient as a PCSE user', async () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
            mockedUsePatient.mockReturnValue(buildPatientDetails({ deceased: true }));

            renderComponent();

            act(() => {
                userEvent.click(screen.getByTestId('go-back-button'));
            });

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith(routes.VERIFY_PATIENT);
            });
        });
    });
});
const TestApp = (props: Omit<Props, 'setStage' | 'stage'>) => {
    let history = createMemoryHistory({
        initialEntries: ['/'],
        initialIndex: 0,
    });

    return (
        <ReactRouter.Router navigator={history} location={history.location}>
            <LloydGeorgeViewRecordStage
                {...props}
                setStage={mockSetStage}
                stage={LG_RECORD_STAGE.RECORD}
            />
        </ReactRouter.Router>
    );
};

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage' | 'stage'> = {
        downloadStage: DOWNLOAD_STAGE.SUCCEEDED,
        lastUpdated: mockPdf.lastUpdated,
        refreshRecord: vi.fn(),
        cloudFrontUrl: 'http://test.com',
        showMenu: true,
        resetDocState: vi.fn(),
        ...propsOverride,
    };
    render(
        <SessionProvider sessionOverride={{ isLoggedIn: true }}>
            <TestApp {...props} />
        </SessionProvider>,
    );
};
