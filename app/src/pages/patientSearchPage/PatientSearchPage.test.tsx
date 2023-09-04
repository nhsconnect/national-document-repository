import { render, screen, waitFor } from '@testing-library/react';
import { USER_ROLE } from '../../types/generic/roles';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { PatientDetails } from '../../types/generic/patientDetails';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import PatientSearchPage from './PatientSearchPage';
import userEvent from '@testing-library/user-event';

describe('PatientSearchPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('displays component', () => {
            renderPatientSearchPage();
            expect(screen.getByText('Search for patient')).toBeInTheDocument();
            expect(screen.getByRole('textbox', { name: 'Enter NHS number' })).toBeInTheDocument();
            expect(
                screen.getByText('A 10-digit number, for example, 485 777 3456'),
            ).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
        });

        it('displays a loading spinner when the patients details are being requested', async () => {
            const getPatientDetailsMock = jest.fn();
            getPatientDetailsMock.mockResolvedValue([]);

            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000009');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(screen.getByRole('SpinnerButton')).toBeInTheDocument();
            });

            expect(screen.getByText('Searching...')).toBeInTheDocument();
        });

        it('displays a validation error when invalid NHS number provided', async () => {
            renderPatientSearchPage();
            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '21212');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));
            await waitFor(() => {
                expect(
                    screen.getByText("Please enter patient's 10 digit NHS number"),
                ).toBeInTheDocument();
            });
        });

        // it('displays server error message when server is down', async () => {
        //     const getPatientDetailsMock = jest.fn();
        //     getPatientDetailsMock.mockRejectedValue(null);

        //     renderPatientSearchPage();
        //     userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '0987654321');
        //     userEvent.click(screen.getByRole('button', { name: 'Search' }));
        //     await waitFor(() => {
        //         expect(
        //             screen.getByText('Sorry, the service is currently unavailable.'),
        //         ).toBeInTheDocument();
        //     });
        // });
    });

    describe('Navigation', () => {});
});

const homeRoute = '/example';
const renderPatientSearchPage = (
    patientOverride: Partial<PatientDetails> = {},
    role: USER_ROLE = USER_ROLE.PCSE,
    history = createMemoryHistory({
        initialEntries: [homeRoute],
        initialIndex: 1,
    }),
) => {
    render(
        <ReactRouter.Router navigator={history} location={homeRoute}>
            <PatientDetailsProvider>
                <PatientSearchPage role={role} />
            </PatientDetailsProvider>
        </ReactRouter.Router>,
    );
};
