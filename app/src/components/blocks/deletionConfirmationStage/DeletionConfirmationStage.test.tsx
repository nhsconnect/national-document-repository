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
import { USER_ROLE } from '../../../types/generic/roles';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import { routes } from '../../../types/generic/routes';

const mockPatientDetails = buildPatientDetails();
const mockLgSearchResult = buildLgSearchResult();
const mockSetStage = jest.fn();

describe('DeletionConfirmationStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('GP USER', () => {
        it('renders the page with patient details', async () => {
            const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
            const numberOfFiles = mockLgSearchResult.number_of_files;

            renderComponent(USER_ROLE.GP, numberOfFiles);

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

        it('sets stage back to LgRecordStage when button is clicked', async () => {
            const numberOfFiles = mockLgSearchResult.number_of_files;

            renderComponent(USER_ROLE.GP, numberOfFiles);

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

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

    describe('PCSE USER', () => {
        it('renders the page with patient details', async () => {
            const patientName = `${mockPatientDetails.givenName} ${mockPatientDetails.familyName}`;
            const numberOfFiles = 1;

            renderComponent(USER_ROLE.PCSE, numberOfFiles);

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            expect(
                screen.getByText(`${numberOfFiles} file from the record of:`),
            ).toBeInTheDocument();
            expect(screen.getByText(patientName)).toBeInTheDocument();
            expect(screen.getByText(/NHS number/)).toBeInTheDocument();
            expect(
                screen.getByRole('link', {
                    name: 'Start Again',
                }),
            ).toBeInTheDocument();
        });

        it('navigates to Home page when link is clicked', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/'],
                initialIndex: 0,
            });

            const numberOfFiles = 7;

            renderComponent(USER_ROLE.PCSE, numberOfFiles, history);

            await waitFor(async () => {
                expect(screen.getByText('Deletion complete')).toBeInTheDocument();
            });

            act(() => {
                userEvent.click(
                    screen.getByRole('link', {
                        name: 'Start Again',
                    }),
                );
            });

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.HOME);
            });
        });
    });
});

const renderComponent = (
    userType: USER_ROLE,
    numberOfFiles: number,
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
        <ReactRouter.Router navigator={history} location={'/'}>
            <SessionProvider sessionOverride={auth}>
                <DeletionConfirmationStage
                    numberOfFiles={numberOfFiles}
                    patientDetails={mockPatientDetails}
                    setStage={mockSetStage}
                    userType={userType}
                />
            </SessionProvider>
        </ReactRouter.Router>,
    );
};
