import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import LloydGeorgeSelectDownloadStage from './LloydGeorgeSelectDownloadStage';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';

jest.mock('../../../../helpers/hooks/usePatient');
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));

const mockSetStage = jest.fn();
const mockSetDownloadStage = jest.fn();
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();

describe('LloydGeorgeSelectDownloadStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header, patient details and loading text', () => {
        render(
            <LloydGeorgeSelectDownloadStage
                setStage={mockSetStage}
                setDownloadStage={mockSetDownloadStage}
            />,
        );

        expect(
            screen.getByRole('heading', {
                name: 'Download the Lloyd George record for this patient',
            }),
        ).toBeInTheDocument();
        expect(screen.getByText('NHS number')).toBeInTheDocument();
        expect(screen.getByText(`${mockPatient.nhsNumber}`)).toBeInTheDocument();
        expect(screen.getByText('Surname')).toBeInTheDocument();
        expect(screen.getByText(`${mockPatient.familyName}`)).toBeInTheDocument();
        expect(screen.getByText('First name')).toBeInTheDocument();
        expect(screen.getByText(`${mockPatient.givenName}`)).toBeInTheDocument();
        expect(screen.getByText('Date of birth')).toBeInTheDocument();
        expect(
            screen.getByText(getFormattedDate(new Date(mockPatient.birthDate))),
        ).toBeInTheDocument();
        expect(screen.getByText('Postcode')).toBeInTheDocument();
        expect(screen.getByText(`${mockPatient.postalCode}`)).toBeInTheDocument();

        expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
});
