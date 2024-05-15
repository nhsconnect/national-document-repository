import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import { routes } from '../../../../types/generic/routes';
import LgDownloadComplete from './LloydGeorgeDownloadComplete';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { act } from 'react-dom/test-utils';

jest.mock('../../../../helpers/hooks/usePatient');

const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();

jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));

describe('LloydGeorgeDownloadComplete', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the component', () => {
        render(<LgDownloadComplete deleteAfterDownload={false} />);

        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
        expect(
            screen.getByText('You have successfully downloaded the Lloyd George record of:'),
        ).toBeInTheDocument();
        expect(
            screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: "Return to patient's available medical records" }),
        ).toBeInTheDocument();
    });

    it('navigates to the view Lloyd George page when back to medical records is clicked', async () => {
        render(<LgDownloadComplete deleteAfterDownload={false} />);

        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
        expect(
            screen.getByText('You have successfully downloaded the Lloyd George record of:'),
        ).toBeInTheDocument();
        expect(
            screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
        ).toBeInTheDocument();

        const returnToRecordButton = screen.getByRole('button', {
            name: "Return to patient's available medical records",
        });
        expect(returnToRecordButton).toBeInTheDocument();
        expect(
            screen.queryByText('This record has been removed from our storage.'),
        ).not.toBeInTheDocument();

        act(() => {
            userEvent.click(returnToRecordButton);
        });

        await waitFor(async () => {
            expect(mockNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
        });
    });

    it('display record removed text if deleteAfterDownload is true', async () => {
        render(<LgDownloadComplete deleteAfterDownload={true} />);

        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
        expect(
            screen.getByText('You have successfully downloaded the Lloyd George record of:'),
        ).toBeInTheDocument();
        expect(
            screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
        ).toBeInTheDocument();

        expect(
            screen.getByText('This record has been removed from our storage.'),
        ).toBeInTheDocument();
    });
});
