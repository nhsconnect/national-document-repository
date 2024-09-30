import { LinkProps } from 'react-router-dom';
import usePatient from '../../../../helpers/hooks/usePatient';
import {
    buildConfig,
    buildLgSearchResult,
    buildPatientDetails,
} from '../../../../helpers/test/testBuilders';
import useRole from '../../../../helpers/hooks/useRole';
import useIsBSOL from '../../../../helpers/hooks/useIsBSOL';
import useConfig from '../../../../helpers/hooks/useConfig';
import { act, render, screen, waitFor } from '@testing-library/react';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import userEvent from '@testing-library/user-event';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import { routeChildren } from '../../../../types/generic/routes';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import LloydGeorgeViewRecordStage, { Props } from './LloydGeorgeViewRecordStage';
import { createMemoryHistory } from 'history';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import * as ReactRouter from 'react-router-dom';
const mockPdf = buildLgSearchResult();
const mockPatientDetails = buildPatientDetails();
jest.mock('../../../../helpers/hooks/useRole');
jest.mock('../../../../helpers/hooks/usePatient');
jest.mock('../../../../helpers/hooks/useIsBSOL');
jest.mock('../../../../helpers/hooks/useConfig');
jest.mock('../../../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();
const mockedUseRole = useRole as jest.Mock;
const mockedIsBSOL = useIsBSOL as jest.Mock;
const mockSetStage = jest.fn();
const mockUseConfig = useConfig as jest.Mock;

describe('LloydGeorgeViewRecordStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatientDetails);
        mockUseConfig.mockReturnValue(buildConfig());
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders an lg record', async () => {
        renderComponent();

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });

        expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        expect(screen.getByText(`Last updated: ${mockPdf.last_updated}`)).toBeInTheDocument();
        expect(screen.getByText(`${mockPdf.number_of_files} files`)).toBeInTheDocument();
        expect(
            screen.getByText(`File size: ${formatFileSize(mockPdf.total_file_size_in_byte)}`),
        ).toBeInTheDocument();
        expect(screen.getByText('File format: PDF')).toBeInTheDocument();

        expect(
            screen.queryByText('No documents are available for this patient.'),
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
            });

            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
        },
    );

    it('renders no docs available text if there is no LG record', async () => {
        renderComponent({
            downloadStage: DOWNLOAD_STAGE.NO_RECORDS,
        });

        await waitFor(async () => {
            expect(screen.getByText(/No documents are available/i)).toBeInTheDocument();
        });
    });

    it("renders 'full screen' mode correctly", async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
        const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
        const dob = getFormattedDate(new Date(mockPatientDetails.birthDate));

        renderComponent();

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });

        act(() => {
            userEvent.click(screen.getByText('View in full screen'));
        });
        await waitFor(() => {
            expect(screen.queryByText('Lloyd George record')).not.toBeInTheDocument();
        });
        expect(screen.getByText('Exit full screen')).toBeInTheDocument();
        expect(screen.getByText(patientName)).toBeInTheDocument();
        expect(screen.getByText(`Date of birth: ${dob}`)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
    });

    it("returns to previous view when 'Go back' link clicked during full screen", async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
        renderComponent();
        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });

        act(() => {
            userEvent.click(screen.getByText('View in full screen'));
        });
        await waitFor(() => {
            expect(screen.queryByText('Lloyd George record')).not.toBeInTheDocument();
        });

        act(() => {
            userEvent.click(screen.getByText('Exit full screen'));
        });

        await waitFor(() => {
            expect(screen.getByText('Lloyd George record')).toBeInTheDocument();
        });
    });

    describe('User is GP admin and non BSOL', () => {
        const renderComponentForNonBSOLGPAdmin = () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            mockedIsBSOL.mockReturnValue(false);
            renderComponent();
        };

        const showConfirmationMessage = async () => {
            const sideMenuDownloadButton = screen.getByRole('button', {
                name: 'Download and remove files',
            });

            act(() => {
                userEvent.click(sideMenuDownloadButton);
            });
            await waitFor(() => {
                expect(
                    screen.getByText('Are you sure you want to download and remove this record?'),
                ).toBeInTheDocument();
            });
        };

        const clickRedDownloadButton = () => {
            const redDownloadButton = screen.getByRole('button', {
                name: 'Yes, download and remove',
            });

            act(() => {
                userEvent.click(redDownloadButton);
            });
        };

        it('renders warning callout, header and button', async () => {
            renderComponentForNonBSOLGPAdmin();

            expect(screen.getByText('Before downloading')).toBeInTheDocument();
            expect(screen.getByText('Available records')).toBeInTheDocument();
            expect(screen.getByTestId('download-and-remove-record-btn')).toBeInTheDocument();
        });

        it('clicking the side menu download button should show confirmation message, checkbox, red download button and cancel button', async () => {
            renderComponentForNonBSOLGPAdmin();

            const downloadButton = screen.getByTestId('download-and-remove-record-btn');

            act(() => {
                userEvent.click(downloadButton);
            });

            await waitFor(() => {
                expect(
                    screen.getByText('Are you sure you want to download and remove this record?'),
                ).toBeInTheDocument();
            });
            expect(
                screen.getByText(
                    "If you download this record, it removes from our storage. You must keep the patient's record safe.",
                ),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('checkbox', {
                    name: 'I understand that downloading this record removes it from storage.',
                }),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Yes, download and remove' }),
            ).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
        });

        it('when checkbox is unchecked, clicking red download button should show an alert and not allowing download', async () => {
            renderComponentForNonBSOLGPAdmin();
            await showConfirmationMessage();

            clickRedDownloadButton();

            await waitFor(() => {
                expect(
                    screen.getByRole('alert', { name: 'There is a problem' }),
                ).toBeInTheDocument();
            });
            expect(
                screen.getByText('You must confirm if you want to download and remove this record'),
            ).toBeInTheDocument();
            expect(
                screen.getByText('Confirm if you want to download and remove this record'),
            ).toBeInTheDocument();
            expect(mockSetStage).not.toBeCalled();
        });

        it('when checkbox is unchecked, clicking "Download and remove" button twice will bring up a warning callout message', async () => {
            renderComponentForNonBSOLGPAdmin();
            await showConfirmationMessage();

            act(() => {
                userEvent.click(
                    screen.getByRole('button', {
                        name: 'Download and remove files',
                    }),
                );
            });

            expect(
                screen.getByText('You must confirm if you want to download and remove this record'),
            ).toBeInTheDocument();
            expect(
                screen.getByText('Confirm if you want to download and remove this record'),
            ).toBeInTheDocument();
            expect(mockSetStage).not.toBeCalled();
        });

        it('when checkbox is checked, clicking red download button should proceed to download and delete process', async () => {
            renderComponentForNonBSOLGPAdmin();
            await showConfirmationMessage();

            act(() => {
                userEvent.click(screen.getByRole('checkbox'));
            });

            clickRedDownloadButton();

            await waitFor(() => {
                expect(mockNavigate).toBeCalledWith(
                    routeChildren.LLOYD_GEORGE_DOWNLOAD_IN_PROGRESS,
                );
            });
        });

        it('when checkbox is toggled 2 times ( = unchecked), red download button should not proceed to download', async () => {
            renderComponentForNonBSOLGPAdmin();
            await showConfirmationMessage();

            const checkBox = screen.getByRole('checkbox');
            act(() => {
                userEvent.click(checkBox);
                userEvent.click(checkBox);
            });

            clickRedDownloadButton();

            await waitFor(() => {
                expect(
                    screen.getByRole('alert', { name: 'There is a problem' }),
                ).toBeInTheDocument();
            });
            expect(mockSetStage).not.toBeCalled();
        });

        it('clicking cancel button will hide the confirmation message', async () => {
            renderComponentForNonBSOLGPAdmin();
            await showConfirmationMessage();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
            });

            await waitFor(() => {
                expect(
                    screen.queryByText('Are you sure you want to download and remove this record?'),
                ).not.toBeInTheDocument();
            });
        });

        describe('Accessibility (non BSOL)', () => {
            it('pass accessibility checks at page entry point', async () => {
                renderComponentForNonBSOLGPAdmin();

                const results = await runAxeTest(document.body);
                expect(results).toHaveNoViolations();
            });

            it('pass accessibility checks when Download & Remove confirmation message is showing up', async () => {
                renderComponentForNonBSOLGPAdmin();
                await showConfirmationMessage();

                const results = await runAxeTest(document.body);
                expect(results).toHaveNoViolations();
            });

            it('pass accessibility checks when error box is showing up', async () => {
                renderComponentForNonBSOLGPAdmin();
                await showConfirmationMessage();
                const confirmButton = await screen.findByRole('button', {
                    name: 'Yes, download and remove',
                });
                act(() => {
                    userEvent.click(confirmButton);
                });
                expect(
                    await screen.findByText(
                        'Confirm if you want to download and remove this record',
                    ),
                ).toBeInTheDocument();

                // to supress act() warning from non-captured classname change
                // eslint-disable-next-line testing-library/no-node-access
                const fieldsetParentDiv = screen.getByTestId('fieldset').closest('div');
                await waitFor(() => {
                    expect(fieldsetParentDiv).toHaveClass('nhsuk-form-group--error');
                });

                const results = await runAxeTest(document.body);
                expect(results).toHaveNoViolations();
            });
        });
    });

    it('does not render warning callout or button when user is GP admin and BSOL', async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
        mockedIsBSOL.mockReturnValue(true);

        renderComponent();

        expect(screen.queryByText('Before downloading')).not.toBeInTheDocument();
        expect(
            screen.queryByRole('button', { name: 'Download and remove files' }),
        ).not.toBeInTheDocument();
    });

    it('does not render warning callout or button when user is GP clinical and non BSOL', async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
        mockedIsBSOL.mockReturnValue(false);

        renderComponent();

        expect(screen.queryByText('Before downloading')).not.toBeInTheDocument();
        expect(
            screen.queryByRole('button', { name: 'Download and remove files' }),
        ).not.toBeInTheDocument();
    });

    it('does not render warning callout or button when user is GP clinical and BSOL', async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
        mockedIsBSOL.mockReturnValue(true);

        renderComponent();

        expect(screen.queryByText('Before downloading')).not.toBeInTheDocument();
        expect(
            screen.queryByRole('button', { name: 'Download and remove files' }),
        ).not.toBeInTheDocument();
    });

    describe('Accessibility (in BSOL)', () => {
        it('pass accessibility checks when no LG record are displayed', async () => {
            renderComponent({
                downloadStage: DOWNLOAD_STAGE.NO_RECORDS,
            });

            expect(await screen.findByText(/No documents are available/)).toBeInTheDocument();

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
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
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
        lastUpdated: mockPdf.last_updated,
        numberOfFiles: mockPdf.number_of_files,
        totalFileSizeInByte: mockPdf.total_file_size_in_byte,
        refreshRecord: jest.fn(),
        cloudFrontUrl: 'http://test.com',
        ...propsOverride,
    };
    render(<TestApp {...props} />);
};
