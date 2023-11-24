import { render, waitFor } from '@testing-library/react';
import { routes } from '../../../types/generic/routes';
import PatientGuard from './PatientGuard';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import usePatient from '../../../helpers/hooks/usePatient';

const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as jest.Mock;
const patientDetails = buildPatientDetails();

describe('AuthGuard', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('navigates user to unauthorised when no patient is searched', async () => {
        mockedUsePatient.mockReturnValue(null);

        renderGuard();

        await waitFor(async () => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED);
        });
    });

    it('navigates user to correct page when patient is searched', async () => {
        mockedUsePatient.mockReturnValue(patientDetails);

        renderGuard();

        await waitFor(async () => {
            expect(mockedUseNavigate).not.toHaveBeenCalled();
        });
    });
});

const renderGuard = () => {
    return render(
        <PatientGuard>
            <div>patient number: {patientDetails?.nhsNumber}</div>
            <div>patient postcode: {patientDetails?.postalCode}</div>
        </PatientGuard>,
    );
};
