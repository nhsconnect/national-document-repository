import { render, screen } from '@testing-library/react';
import usePatient from '../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import { useState } from 'react';
import LloydGeorgeUploadPage, { LG_UPLOAD_STAGE } from './LloydGeorgeUploadPage';
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
jest.mock(
    '../../components/blocks/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage',
    () => () => <h1>Mock file input stage</h1>,
);
jest.mock(
    '../../components/blocks/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage',
    () => () => <h1>Mock files are uploading stage</h1>,
);
jest.mock(
    '../../components/blocks/lloydGeorgeUploadCompleteStage/LloydGeorgeUploadCompleteStage',
    () => () => <h1>Mock complete stage</h1>,
);

describe('UploadDocumentsPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
        mockUseState.mockImplementation(() => [LG_UPLOAD_STAGE.SELECT, jest.fn()]);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders initial file input stage', () => {
            render(<LloydGeorgeUploadPage />);
            expect(
                screen.getByRole('heading', { name: 'Mock file input stage' }),
            ).toBeInTheDocument();
        });

        it('renders uploading stage when state is set', () => {
            mockUseState.mockImplementation(() => [LG_UPLOAD_STAGE.UPLOAD, jest.fn()]);
            render(<LloydGeorgeUploadPage />);
            expect(
                screen.getByRole('heading', { name: 'Mock files are uploading stage' }),
            ).toBeInTheDocument();
        });

        it('renders upload complete stage when state is set', () => {
            mockUseState.mockImplementation(() => [LG_UPLOAD_STAGE.COMPLETE, jest.fn()]);
            render(<LloydGeorgeUploadPage />);
            expect(
                screen.getByRole('heading', { name: 'Mock complete stage' }),
            ).toBeInTheDocument();
        });
    });
    describe('Navigation', () => {});
});
