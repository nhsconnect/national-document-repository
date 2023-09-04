import { render, screen, waitFor } from '@testing-library/react';
import { USER_ROLE } from '../../types/generic/roles';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { PatientDetails } from '../../types/generic/patientDetails';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import PatientSearchPage from './PatientSearchPage';
import userEvent from '@testing-library/user-event';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import axios from 'axios';
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

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
            mockedAxios.get.mockImplementation(async () => {
                await new Promise((resolve) => {
                    setTimeout(() => {
                        resolve(null);
                    }, 500);
                });
                return Promise.resolve({ data: buildPatientDetails() });
            });

            renderPatientSearchPage();

            userEvent.type(screen.getByRole('textbox', { name: 'Enter NHS number' }), '9000000009');
            userEvent.click(screen.getByRole('button', { name: 'Search' }));

            await waitFor(() => {
                expect(screen.getByRole('SpinnerButton')).toBeInTheDocument();
            });
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
