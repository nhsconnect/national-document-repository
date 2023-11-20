import { render, waitFor } from '@testing-library/react';
import * as ReactRouter from 'react-router';
import { History, createMemoryHistory } from 'history';
import { routes } from '../../../types/generic/routes';
import PatientGuard from './PatientGuard';
import { PatientDetails } from '../../../types/generic/patientDetails';
import PatientDetailsProvider from '../../../providers/patientProvider/PatientProvider';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';

const guardPage = '/profile';
describe('AuthGuard', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('navigates user to unauthorised when no patient is searched', async () => {
        const patientDetails = null;
        const history = createMemoryHistory({
            initialEntries: [guardPage],
            initialIndex: 0,
        });
        expect(history.location.pathname).toBe(guardPage);
        renderAuthGuard(patientDetails, history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(routes.UNAUTHORISED);
        });
    });

    it('navigates user to correct page when patient is searched', async () => {
        const patientDetails = buildPatientDetails();
        const history = createMemoryHistory({
            initialEntries: [guardPage],
            initialIndex: 0,
        });
        expect(history.location.pathname).toBe(guardPage);
        renderAuthGuard(patientDetails, history);

        await waitFor(async () => {
            expect(history.location.pathname).toBe(guardPage);
        });
    });
});

const renderAuthGuard = (patient: PatientDetails | null, history: History) => {
    return render(
        <PatientDetailsProvider patientDetails={patient}>
            <ReactRouter.Router navigator={history} location={history.location}>
                <PatientGuard>
                    <div>patient number: {patient?.nhsNumber}</div>
                    <div>patient postcode: {patient?.postalCode}</div>
                </PatientGuard>
            </ReactRouter.Router>
            ,
        </PatientDetailsProvider>,
    );
};
