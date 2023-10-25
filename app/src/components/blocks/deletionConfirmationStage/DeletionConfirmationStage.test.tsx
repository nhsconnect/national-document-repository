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
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import { USER_ROLE } from '../../../types/generic/roles';

const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();
const mockSetStage = jest.fn();
const mockNavigateCallback = jest.fn();

describe('DeletionConfirmationStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    it('renders the page with patient details', async () => {
        const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
        const numberOfFiles = mockLgSearchResult.number_of_files;

        renderComponent(USER_ROLE.GP);

        await waitFor(async () => {
            expect(screen.getByText('Deletion complete')).toBeInTheDocument();
        });

        expect(
            screen.getByText(`${numberOfFiles} files from the Lloyd George record of:`),
        ).toBeInTheDocument();
        expect(screen.getByText(patientName)).toBeInTheDocument();
        expect(screen.getByText(/NHS number/)).toBeInTheDocument();
        expect(
            screen.getByRole('button', {
                name: "Return to patient's Lloyd George record page",
            }),
        ).toBeInTheDocument();
    });

    it('renders LgRecordStage when button is clicked', async () => {
        renderComponent(USER_ROLE.GP);

        act(() => {
            userEvent.click(
                screen.getByRole('button', {
                    name: "Return to patient's Lloyd George record page",
                }),
            );
        });

        await waitFor(() => {
            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.RECORD);
        });
    });
});

const renderComponent = (
    userType: USER_ROLE,
    history = createMemoryHistory({
        initialEntries: ['/'],
        initialIndex: 0,
    }),
) => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };
    render(
        <ReactRouter.Router navigator={history} location={history.location}>
            <SessionProvider sessionOverride={auth}>
                <DeletionConfirmationStage
                    numberOfFiles={mockLgSearchResult.number_of_files}
                    patientDetails={mockPatientDetails}
                    setStage={mockSetStage}
                    userType={userType}
                    passNavigate={mockNavigateCallback}
                />
            </SessionProvider>
        </ReactRouter.Router>,
    );
};
