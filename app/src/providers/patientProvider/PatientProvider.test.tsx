import { fireEvent, render, screen } from '@testing-library/react';
import PatientDetailsProvider, { usePatientDetailsContext } from './PatientProvider';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import type { PatientDetails } from '../../types/generic/patientDetails';

describe('PatientDetailsProvider', () => {
    it('provides NHS number and family name', () => {
        const patientDetails = buildPatientDetails({
            nhsNumber: '0000012007',
            familyName: 'Smith',
        });

        render(
            <PatientDetailsProvider>
                <TestComponent patientDetails={patientDetails} />
            </PatientDetailsProvider>,
        );

        expect(screen.getByText('NHS Number: Null')).toBeInTheDocument();
        expect(screen.getByText('Family Name: Null')).toBeInTheDocument();

        fireEvent.click(screen.getByRole('button', { name: 'Update NHS Number' }));

        expect(screen.getByText(`Family Name: ${patientDetails.familyName}`)).toBeInTheDocument();
        expect(screen.getByText(`NHS Number: ${patientDetails.nhsNumber}`)).toBeInTheDocument();
    });
});

type TestProps = {
    patientDetails: PatientDetails;
};

const TestComponent = (props: TestProps) => {
    const [patientDetails, setPatientDetails] = usePatientDetailsContext();

    return (
        <>
            <p>NHS Number: {patientDetails?.nhsNumber ?? 'Null'}</p>
            <p>Family Name: {patientDetails?.familyName || 'Null'}</p>
            <button onClick={() => setPatientDetails(props.patientDetails)}>
                Update NHS Number
            </button>
        </>
    );
};
