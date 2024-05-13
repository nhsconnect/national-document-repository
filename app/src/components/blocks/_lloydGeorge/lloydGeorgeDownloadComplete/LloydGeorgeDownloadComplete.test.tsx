import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import { render, screen, waitFor } from '@testing-library/react';
import LloydGeorgeDownloadComplete from './LloydGeorgeDownloadComplete';

jest.mock('../../../../helpers/hooks/usePatient');

const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNumberOfFiles = 7;

describe('LloydGeorgeDownloadComplete', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('LloydGeorgeDownloadComplete non BSOL journey', () => {
        it('renders the component', () => {
            render(
                <LloydGeorgeDownloadComplete
                    deleteAfterDownload={false}
                    numberOfFiles={mockNumberOfFiles}
                />,
            );

            expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
            expect(
                screen.getByText('You have successfully downloaded the Lloyd George record of:'),
            ).toBeInTheDocument();
            expect(
                screen.getByText(mockPatient.givenName + ' ' + mockPatient.familyName),
            ).toBeInTheDocument();
        });

        it('display record removed text if deleteAfterDownload is true', async () => {
            render(
                <LloydGeorgeDownloadComplete
                    deleteAfterDownload={true}
                    numberOfFiles={mockNumberOfFiles}
                />,
            );

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

    describe('LloydGeorgeDownloadComplete BSOL journeys', () => {});
});
