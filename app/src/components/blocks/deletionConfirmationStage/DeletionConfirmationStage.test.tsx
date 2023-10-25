import { render, screen, waitFor } from '@testing-library/react';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import {
    buildLgSearchResult,
    buildPatientDetails,
    buildUserAuth,
} from '../../../helpers/test/testBuilders';
import DeletionConfirmationStage from './DeletionConfirmationStage';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';

const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();
const mockSetStage = jest.fn();

describe('DeletionConfirmationStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    it('renders the page with patient details', async () => {
        const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
        const numberOfFiles = mockLgSearchResult.number_of_files;

        renderPage();

        await waitFor(async () => {
            expect(screen.getByText('Deletion complete')).toBeInTheDocument();
        });

        expect(
            screen.getByText(`${numberOfFiles} files from the Lloyd George record of:`)
        ).toBeInTheDocument();
        expect(screen.getByText(patientName)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
        expect(
            screen.getByRole('button', {
                name: "Return to patient's Lloyd George record page",
            })
        ).toBeInTheDocument();
    });

    it('renders LgRecordStage when button is clicked', async () => {
        renderPage();

        act(() => {
            userEvent.click(
                screen.getByRole('button', {
                    name: "Return to patient's Lloyd George record page",
                })
            );
        });

        await waitFor(() => {
            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
        });
    });
});

const renderPage = () => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };
    render(
        <SessionProvider sessionOverride={auth}>
            <DeletionConfirmationStage
                numberOfFiles={mockLgSearchResult.number_of_files}
                patientDetails={mockPatientDetails}
                setStage={mockSetStage}
            />
        </SessionProvider>
    );
};
