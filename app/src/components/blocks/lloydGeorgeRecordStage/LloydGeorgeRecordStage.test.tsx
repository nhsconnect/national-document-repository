import { render, screen, waitFor } from '@testing-library/react';
import { buildLgSearchResult, buildPatientDetails } from '../../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import LgRecordStage, { Props } from './LloydGeorgeRecordStage';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import { useState } from 'react';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import { act } from 'react-dom/test-utils';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../helpers/hooks/usePatient';
import useRole from '../../../helpers/hooks/useRole';
import useIsBSOL from '../../../helpers/hooks/useIsBSOL';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';

const mockPdf = buildLgSearchResult();
const mockPatientDetails = buildPatientDetails();

jest.mock('../../../helpers/hooks/useRole');
jest.mock('../../../helpers/hooks/usePatient');
jest.mock('../../../helpers/hooks/useIsBSOL');
const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();
const mockedUseRole = useRole as jest.Mock;
const mockedIsBSOL = useIsBSOL as jest.Mock;
const mockSetStage = jest.fn();

jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));

describe('LloydGeorgeRecordStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatientDetails);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders an lg record', async () => {
        renderComponent();

        await waitFor(() => {
            expect(screen.getByTitle('Embedded PDF')).toBeInTheDocument();
        });
        expect(screen.getByText('View record')).toBeInTheDocument();
        expect(screen.getByText('View in full screen')).toBeInTheDocument();

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

    it('renders no docs available text if there is no LG record', async () => {
        renderComponent({
            downloadStage: DOWNLOAD_STAGE.NO_RECORDS,
        });

        await waitFor(async () => {
            expect(screen.getByText(/No documents are available/i)).toBeInTheDocument();
        });

        expect(screen.queryByText('View record')).not.toBeInTheDocument();
    });

    it("renders 'full screen' mode correctly", async () => {
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
        expect(screen.getByText('Go back')).toBeInTheDocument();
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
            expect(screen.queryByText('Lloyd George record')).not.toBeInTheDocument();
        });

        act(() => {
            userEvent.click(screen.getByText('Go back'));
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
            const greenDownloadButton = screen.getByRole('button', {
                name: 'Download and remove record',
            });

            act(() => {
                userEvent.click(greenDownloadButton);
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
            expect(
                screen.getByRole('button', { name: 'Download and remove record' }),
            ).toBeInTheDocument();
        });

        it('clicking the green download button should show confirmation message, checkbox, red download button and cancel button', async () => {
            renderComponentForNonBSOLGPAdmin();

            const downloadButton = screen.getByRole('button', {
                name: 'Download and remove record',
            });

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

        it('when checkbox is checked, clicking red download button should proceed to download and delete process', async () => {
            renderComponentForNonBSOLGPAdmin();
            await showConfirmationMessage();

            act(() => {
                userEvent.click(screen.getByRole('checkbox'));
            });

            clickRedDownloadButton();

            await waitFor(() => {
                expect(mockSetStage).toBeCalledWith(LG_RECORD_STAGE.DOWNLOAD_ALL);
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
    });

    it('does not render warning callout, header and button when user is GP admin and BSOL', async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
        mockedIsBSOL.mockReturnValue(true);

        renderComponent();

        expect(screen.queryByText('Before downloading')).not.toBeInTheDocument();
        expect(screen.queryByText('Available records')).not.toBeInTheDocument();
        expect(
            screen.queryByRole('button', { name: 'Download and remove record' }),
        ).not.toBeInTheDocument();
    });

    it('does not render warning callout, header and button when user is GP clinical and non BSOL', async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
        mockedIsBSOL.mockReturnValue(false);

        renderComponent();

        expect(screen.queryByText('Before downloading')).not.toBeInTheDocument();
        expect(screen.queryByText('Available records')).not.toBeInTheDocument();
        expect(
            screen.queryByRole('button', { name: 'Download and remove record' }),
        ).not.toBeInTheDocument();
    });

    it('does not render warning callout, header and button when user is GP clinical and BSOL', async () => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
        mockedIsBSOL.mockReturnValue(true);

        renderComponent();

        expect(screen.queryByText('Before downloading')).not.toBeInTheDocument();
        expect(screen.queryByText('Available records')).not.toBeInTheDocument();
        expect(
            screen.queryByRole('button', { name: 'Download and remove record' }),
        ).not.toBeInTheDocument();
    });
});
const TestApp = (props: Omit<Props, 'setStage' | 'stage'>) => {
    return <LgRecordStage {...props} setStage={mockSetStage} stage={LG_RECORD_STAGE.RECORD} />;
};

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage' | 'stage'> = {
        downloadStage: DOWNLOAD_STAGE.SUCCEEDED,
        lloydGeorgeUrl: mockPdf.presign_url,
        lastUpdated: mockPdf.last_updated,
        numberOfFiles: mockPdf.number_of_files,
        totalFileSizeInByte: mockPdf.total_file_size_in_byte,

        ...propsOverride,
    };
    render(<TestApp {...props} />);
};
