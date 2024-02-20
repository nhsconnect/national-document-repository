import { render, screen } from '@testing-library/react';
import UploadDocumentsPage from './UploadDocumentsPage';
import usePatient from '../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import { UPLOAD_STAGE } from '../../types/pages/UploadDocumentsPage/types';
import { useState } from 'react';
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../helpers/hooks/usePatient');
jest.mock('react-router');
const mockedUsePatient = usePatient as jest.Mock;
const mockUseState = useState as jest.Mock;

const mockPatient = buildPatientDetails();
jest.mock('react', () => ({
    ...jest.requireActual('react'),
    useState: jest.fn(),
}));
jest.mock('../../components/blocks/_arf/selectStage/SelectStage', () => () => (
    <h1>Mock file input stage</h1>
));
jest.mock('../../components/blocks/_arf/uploadingStage/UploadingStage', () => () => (
    <h1>Mock files are uploading stage</h1>
));
jest.mock('../../components/blocks/_arf/completeStage/CompleteStage', () => () => (
    <h1>Mock complete stage</h1>
));

describe('UploadDocumentsPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
        mockUseState.mockImplementation(() => [UPLOAD_STAGE.Selecting, jest.fn()]);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders initial file input stage', () => {
            render(<UploadDocumentsPage />);
            expect(
                screen.getByRole('heading', { name: 'Mock file input stage' }),
            ).toBeInTheDocument();
        });

        it('renders uploading stage when state is set', () => {
            mockUseState.mockImplementation(() => [UPLOAD_STAGE.Uploading, jest.fn()]);
            render(<UploadDocumentsPage />);
            expect(
                screen.getByRole('heading', { name: 'Mock files are uploading stage' }),
            ).toBeInTheDocument();
        });

        it('renders upload complete stage when state is set', () => {
            mockUseState.mockImplementation(() => [UPLOAD_STAGE.Complete, jest.fn()]);
            render(<UploadDocumentsPage />);
            expect(
                screen.getByRole('heading', { name: 'Mock complete stage' }),
            ).toBeInTheDocument();
        });
    });
    describe('Navigation', () => {});
});
