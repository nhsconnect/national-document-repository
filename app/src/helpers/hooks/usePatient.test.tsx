import { render, screen } from '@testing-library/react';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { PatientDetails } from '../../types/generic/patientDetails';
import usePatient from './usePatient';
import { buildPatientDetails } from '../test/testBuilders';

describe('usePatient', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('returns patient details when there is a patient in context', () => {
        const patientDetails = buildPatientDetails();
        renderHook(patientDetails);
        expect(screen.getByText(`PATIENT: ${patientDetails.nhsNumber}`)).toBeInTheDocument();
    });

    it('returns null when there is no patient in cont ext', () => {
        renderHook();
        expect(screen.getByText(`PATIENT: null`)).toBeInTheDocument();
    });
});

const TestApp = () => {
    const patient = usePatient();
    return <div>{`PATIENT: ${patient?.nhsNumber ?? null}`.normalize()}</div>;
};

const renderHook = (patient?: PatientDetails) => {
    return render(
        <PatientDetailsProvider patientDetails={patient}>
            <TestApp />
        </PatientDetailsProvider>,
    );
};
