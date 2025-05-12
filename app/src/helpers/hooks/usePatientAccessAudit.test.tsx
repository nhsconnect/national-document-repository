import { render, screen } from '@testing-library/react';
import PatientAccessAuditProvider from '../../providers/patientAccessAuditProvider/PatientAccessAuditProvider';
import { PatientAccessAudit } from '../../types/generic/accessAudit';
import usePatientAccessAudit from './usePatientAccessAudit';
import { buildPatientAccessAudit } from '../test/testBuilders';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

describe('usePatient', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('returns patient access audit details when it is in the context', () => {
        const patientAccessAudit = buildPatientAccessAudit();
        renderHook(patientAccessAudit);
        patientAccessAudit.forEach((audit) => {
            expect(screen.getByText(`PATIENT: ${audit.nhsNumber}`)).toBeInTheDocument();
        });
    });

    it('returns no audit data when there is no patient access audit in the context', () => {
        renderHook();
        expect(screen.getByText('no access audit data')).toBeInTheDocument();
    });
});

const TestApp = () => {
    const patientAccessAudit = usePatientAccessAudit();
    const AccessAudit = patientAccessAudit?.map((audit) => {
        return (
            <div key={audit.nhsNumber}>
                <div>PATIENT: {audit.nhsNumber}</div>
                <div>{audit.accessAuditData.Reasons.join(',')}</div>
                <div>{audit.accessAuditType}</div>
            </div>
        );
    }) ?? <div>no access audit data</div>;
    return <>{AccessAudit}</>;
};

const renderHook = (patientAccessAudit?: PatientAccessAudit[]) => {
    return render(
        <PatientAccessAuditProvider patientAccessAudit={patientAccessAudit}>
            <TestApp />
        </PatientAccessAuditProvider>,
    );
};
