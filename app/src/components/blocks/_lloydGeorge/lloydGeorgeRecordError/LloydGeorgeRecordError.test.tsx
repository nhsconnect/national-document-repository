import { act, render, screen } from '@testing-library/react';
import LloydGeorgeRecordError from './LloydGeorgeRecordError';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import { LinkProps } from 'react-router-dom';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import { routeChildren, routes } from '../../../../types/generic/routes';
import useConfig from '../../../../helpers/hooks/useConfig';
import { buildConfig } from '../../../../helpers/test/testBuilders';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../../helpers/hooks/useRole');
vi.mock('../../../../helpers/hooks/useConfig');
vi.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

const mockUseRole = useRole as Mock;
const mockUseConfig = useConfig as Mock;
const mockNavigate = vi.fn();

describe('LloydGeorgeRecordError', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
        mockUseConfig.mockReturnValue(buildConfig());
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it("renders an error when the document download status is 'Timeout'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;
            render(<LloydGeorgeRecordError downloadStage={timeoutStatus} />);

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i),
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
        });

        it("renders an error when the document download status is 'Failed'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.FAILED;
            render(<LloydGeorgeRecordError downloadStage={timeoutStatus} />);

            expect(
                screen.getByText(/Sorry, the service is currently unavailable/i),
            ).toBeInTheDocument();
            expect(
                screen.getByText(/An error has occurred when creating the Lloyd George preview/i),
            ).toBeInTheDocument();
        });

        it("renders a message  when the document download status is 'Uploading'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.UPLOADING;

            render(<LloydGeorgeRecordError downloadStage={timeoutStatus} />);

            expect(
                screen.getByText(
                    /You can view this record once it’s finished uploading. This may take a few minutes./i,
                ),
            ).toBeInTheDocument();
            expect(
                screen.queryByRole('button', { name: 'Upload patient record' }),
            ).not.toBeInTheDocument();
        });

        it("renders a message and upload button when the document download status is 'No records', user is admin and upload flags are enabled", () => {
            const noRecordsStatus = DOWNLOAD_STAGE.NO_RECORDS;
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            mockUseConfig.mockReturnValue(
                buildConfig(
                    {},
                    {
                        uploadLloydGeorgeWorkflowEnabled: true,
                        uploadLambdaEnabled: true,
                    },
                ),
            );

            render(<LloydGeorgeRecordError downloadStage={noRecordsStatus} />);

            expect(screen.getByText(/No records available for this patient/i)).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Upload patient record' }),
            ).toBeInTheDocument();
        });

        it("renders a message but no upload button when the document download status is 'No records', user is admin and upload flags are not enabled", () => {
            const noRecordsStatus = DOWNLOAD_STAGE.NO_RECORDS;

            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            render(<LloydGeorgeRecordError downloadStage={noRecordsStatus} />);

            expect(
                screen.getByText(
                    /This patient does not have a Lloyd George record stored in this service/i,
                ),
            ).toBeInTheDocument();
            expect(
                screen.queryByRole('button', { name: 'Upload patient record' }),
            ).not.toBeInTheDocument();
        });
    });

    describe.skip('Accessibility', () => {
        it('pass accessibility checks for DOWNLOAD_STAGE.TIMEOUT', async () => {
            render(<LloydGeorgeRecordError downloadStage={DOWNLOAD_STAGE.TIMEOUT} />);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks for DOWNLOAD_STAGE.UPLOADING', async () => {
            render(<LloydGeorgeRecordError downloadStage={DOWNLOAD_STAGE.UPLOADING} />);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks for DOWNLOAD_STAGE.NO_RECORDS when user is GP_ADMIN', async () => {
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            mockUseConfig.mockReturnValue(
                buildConfig(
                    {},
                    {
                        uploadLloydGeorgeWorkflowEnabled: true,
                        uploadLambdaEnabled: true,
                    },
                ),
            );
            render(<LloydGeorgeRecordError downloadStage={DOWNLOAD_STAGE.NO_RECORDS} />);

            await screen.findByText(/You can upload full or part of a patient record./);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks for the last catch all failure case', async () => {
            render(<LloydGeorgeRecordError downloadStage={DOWNLOAD_STAGE.FAILED} />);

            await screen.findByText(
                'An error has occurred when creating the Lloyd George preview.',
            );

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it("renders a link that can navigate to the download all stage, when download status is 'Timeout'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;

            render(<LloydGeorgeRecordError downloadStage={timeoutStatus} />);

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i),
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
            expect(
                screen.getByRole('link', {
                    name: 'please download instead',
                }),
            ).toBeInTheDocument();
        });

        it("navigates to the download all stage, when download status is 'Timeout' and the link is clicked: GP_ADMIN", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;

            render(<LloydGeorgeRecordError downloadStage={timeoutStatus} />);

            const downloadLink = screen.getByRole('link', {
                name: 'please download instead',
            });

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i),
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
            expect(downloadLink).toBeInTheDocument();

            act(() => {
                downloadLink.click();
            });

            expect(mockNavigate).toHaveBeenCalledWith(routeChildren.LLOYD_GEORGE_DOWNLOAD);
        });

        it("navigates to unauthorised, when download status is 'Timeout' and the link is clicked: GP_CLINICAL", () => {
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;

            render(<LloydGeorgeRecordError downloadStage={timeoutStatus} />);

            const downloadLink = screen.getByRole('link', {
                name: 'please download instead',
            });

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i),
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
            expect(downloadLink).toBeInTheDocument();

            act(() => {
                downloadLink.click();
            });

            expect(mockNavigate).toBeCalledWith(routes.UNAUTHORISED);
        });

        it("navigates to upload page, when the document download status is 'No records', user is admin and upload flags are enabled", () => {
            const noRecordsStatus = DOWNLOAD_STAGE.NO_RECORDS;
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            mockUseConfig.mockReturnValue(
                buildConfig(
                    {},
                    {
                        uploadLloydGeorgeWorkflowEnabled: true,
                        uploadLambdaEnabled: true,
                    },
                ),
            );

            render(<LloydGeorgeRecordError downloadStage={noRecordsStatus} />);

            const uploadButton = screen.getByRole('button', { name: 'Upload patient record' });
            expect(screen.getByText(/No records available for this patient/i)).toBeInTheDocument();
            expect(uploadButton).toBeInTheDocument();

            act(() => {
                uploadButton.click();
            });

            expect(mockNavigate).toBeCalledWith(routes.LLOYD_GEORGE_UPLOAD);
        });
    });
});
