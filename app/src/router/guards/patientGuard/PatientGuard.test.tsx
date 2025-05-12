import { render, waitFor } from '@testing-library/react';
import { routes } from '../../../types/generic/routes';
import PatientGuard from './PatientGuard';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import usePatient from '../../../helpers/hooks/usePatient';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));
vi.mock('../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as Mock;
const patientDetails = buildPatientDetails();

describe('AuthGuard', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });
    it('navigates user to search patient page when no patient details are stored', async () => {
        mockedUsePatient.mockReturnValue(null);

        renderGuard();

        await waitFor(async () => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
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
