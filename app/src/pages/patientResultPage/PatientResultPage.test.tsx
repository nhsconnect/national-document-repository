import { render, screen } from '@testing-library/react';
import PatientResultPage from './PatientResultPage';
import { USER_ROLE } from '../../types/generic/roles';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import { PatientDetails } from '../../types/generic/patientDetails';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';

describe('PatientResultPage', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders component', () => {
        const mockDetails = buildPatientDetails({
            familyName: 'Jones',
            nhsNumber: '0000222000',
        });

        renderPatientResultPage(mockDetails);

        expect(screen.getByText(mockDetails.nhsNumber)).toBeInTheDocument();
        expect(screen.getByText(mockDetails.familyName)).toBeInTheDocument();
        //expect(screen.getByText(mockDetails.givenName)).toBeInTheDocument()
    });
});

const renderPatientResultPage = (
    patientOverride: Partial<PatientDetails> = {},
    role: USER_ROLE = USER_ROLE.GP,
) => {
    const patient: PatientDetails = {
        ...buildPatientDetails(),
        ...patientOverride,
    };
    const history = createMemoryHistory({
        initialEntries: ['/', '/example'],
        initialIndex: 1,
    });

    render(
        <ReactRouter.Router navigator={history} location={'/example'}>
            <PatientDetailsProvider patientDetails={patient}>
                <PatientResultPage role={role} />
            </PatientDetailsProvider>
        </ReactRouter.Router>,
    );
};
