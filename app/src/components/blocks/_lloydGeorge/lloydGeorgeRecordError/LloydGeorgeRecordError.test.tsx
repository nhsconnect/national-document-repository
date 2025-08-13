import { render, screen } from '@testing-library/react';
import { act } from 'react';
import LloydGeorgeRecordError from './LloydGeorgeRecordError';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import { LinkProps } from 'react-router-dom';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import { routeChildren, routes } from '../../../../types/generic/routes';
import useConfig from '../../../../helpers/hooks/useConfig';
import { buildConfig, buildPatientDetails } from '../../../../helpers/test/testBuilders';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';
import usePatient from '../../../../helpers/hooks/usePatient';
import { PatientDetails } from '../../../../types/generic/patientDetails';

vi.mock('../../../../helpers/hooks/useRole');
vi.mock('../../../../helpers/hooks/useConfig');
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

const mockUseRole = useRole as Mock;
const mockUseConfig = useConfig as Mock;
const mockNavigate = vi.fn();
const mockPatient = usePatient as Mock;
const mockDeceasedPatientDetails: PatientDetails = buildPatientDetails({ deceased: true });

describe('LloydGeorgeRecordError', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
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
                screen.queryByRole('button', { name: 'Upload files for this patient' }),
            ).not.toBeInTheDocument();
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "renders a message and upload button when the document download status is 'No records', user role is '%s' and upload flags are enabled",
            (role) => {
                const noRecordsStatus = DOWNLOAD_STAGE.NO_RECORDS;
                mockUseRole.mockReturnValue(role);
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

                expect(
                    screen.getByText(
                        /This patient does not have a Lloyd George record stored in this service/i,
                    ),
                ).toBeInTheDocument();
                expect(
                    screen.getByRole('button', { name: 'Upload files for this patient' }),
                ).toBeInTheDocument();
            },
        );

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "renders a message but no upload button when the document download status is 'No records', user role is '%s' and upload flags are not enabled",
            (role) => {
                const noRecordsStatus = DOWNLOAD_STAGE.NO_RECORDS;

                mockUseRole.mockReturnValue(role);

                render(<LloydGeorgeRecordError downloadStage={noRecordsStatus} />);

                expect(
                    screen.getByText(
                        /This patient does not have a Lloyd George record stored in this service/i,
                    ),
                ).toBeInTheDocument();
                expect(
                    screen.queryByRole('button', { name: 'Upload files for this patient' }),
                ).not.toBeInTheDocument();
            },
        );

        it("renders a message but no upload button when the document download status is 'No records', user role is PCSE and upload flags are enabled", () => {
            const noRecordsStatus = DOWNLOAD_STAGE.NO_RECORDS;

            mockUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
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

            expect(
                screen.getByText(
                    /This patient does not have a Lloyd George record stored in this service/i,
                ),
            ).toBeInTheDocument();
            expect(
                screen.queryByRole('button', { name: 'Upload files for this patient' }),
            ).not.toBeInTheDocument();
        });

        it.each([REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL])(
            "renders a message but no upload button when the document download status is 'No records', user role is '%s' and upload flags are enabled and patient is deceased",
            (role) => {
                const noRecordsStatus = DOWNLOAD_STAGE.NO_RECORDS;
                mockPatient.mockReturnValue(mockDeceasedPatientDetails);
                mockUseConfig.mockReturnValue(
                    buildConfig(
                        {},
                        {
                            uploadLloydGeorgeWorkflowEnabled: true,
                            uploadLambdaEnabled: true,
                        },
                    ),
                );
                mockUseRole.mockReturnValue(role);

                render(<LloydGeorgeRecordError downloadStage={noRecordsStatus} />);

                expect(
                    screen.getByText(
                        /This patient does not have a Lloyd George record stored in this service/i,
                    ),
                ).toBeInTheDocument();
                expect(
                    screen.queryByRole('button', { name: 'Upload files for this patient' }),
                ).not.toBeInTheDocument();
            },
        );
    });

    describe('Accessibility', () => {
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

        it("navigates to upload page, when the document download status is 'No records', user is gp user and upload flags are enabled", () => {
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

            const uploadButton = screen.getByRole('button', {
                name: 'Upload files for this patient',
            });
            expect(
                screen.getByText(
                    /This patient does not have a Lloyd George record stored in this service/i,
                ),
            ).toBeInTheDocument();
            expect(uploadButton).toBeInTheDocument();

            act(() => {
                uploadButton.click();
            });

            expect(mockNavigate).toBeCalledWith(routes.DOCUMENT_UPLOAD);
        });
    });
});
