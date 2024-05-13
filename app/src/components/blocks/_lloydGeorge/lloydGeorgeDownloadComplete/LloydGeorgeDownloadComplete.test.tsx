import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { act } from 'react-dom/test-utils';
import LloydGeorgeDownloadComplete from './LloydGeorgeDownloadComplete';

jest.mock('../../../../helpers/hooks/usePatient');

const mockSetStage = jest.fn();
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
