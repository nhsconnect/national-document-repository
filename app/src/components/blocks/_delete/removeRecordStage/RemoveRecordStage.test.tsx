import { render, screen } from '@testing-library/react';
import RemoveRecordStage from './RemoveRecordStage';
import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';

const mockUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockUseNavigate,
}));
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../../../helpers/hooks/usePatient');
const mockUsePatient = usePatient as jest.Mock;
const mockPatientDetails = buildPatientDetails();
const mockSetStage = jest.fn();
describe('RemoveRecordStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockUsePatient.mockReturnValue(mockPatientDetails);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('renders the component', () => {
        const recordType = 'Test Record';
        render(<RemoveRecordStage setStage={mockSetStage} recordType={recordType} />);

        expect(
            screen.getByRole('heading', { name: 'Remove this Test Record' }),
        ).toBeInTheDocument();
    });
});
