import { fireEvent, render, screen } from '@testing-library/react';
import { buildPatientAccessAudit } from '../../helpers/test/testBuilders';
import { PatientAccessAudit } from '../../types/generic/accessAudit';
import PatientAccessAuditProvider, {
    usePatientAccessAuditContext,
} from './PatientAccessAuditProvider';
import { describe, expect, it } from 'vitest';

describe('PatientAccessAuditProvider', () => {
    it('provides patient access audit data', () => {
        const patientAccessAudit = buildPatientAccessAudit();

        render(
            <PatientAccessAuditProvider>
                <TestComponent patientAccessAudit={patientAccessAudit} />
            </PatientAccessAuditProvider>,
        );

        expect(screen.getByText('NHS Number: Null')).toBeInTheDocument();
        expect(screen.getByText('Access Audit Type: Null')).toBeInTheDocument();

        fireEvent.click(screen.getByRole('button', { name: 'Update Patient Access Audit' }));

        expect(
            screen.getByText(`NHS Number: ${patientAccessAudit[0].nhsNumber}`),
        ).toBeInTheDocument();
        expect(
            screen.getByText(`Access Audit Type: ${patientAccessAudit[0].accessAuditType}`),
        ).toBeInTheDocument();
    });
});

type TestProps = {
    patientAccessAudit: PatientAccessAudit[];
};

const TestComponent = (props: TestProps) => {
    const [patientAccessAudit, setPatientAccessAudit] = usePatientAccessAuditContext();

    const audit = patientAccessAudit?.[0];

    return (
        <>
            <p>NHS Number: {audit?.nhsNumber ?? 'Null'}</p>
            <p>Access Audit Type: {audit?.accessAuditType ?? 'Null'}</p>
            <button onClick={() => setPatientAccessAudit(props.patientAccessAudit)}>
                Update Patient Access Audit
            </button>
        </>
    );
};
