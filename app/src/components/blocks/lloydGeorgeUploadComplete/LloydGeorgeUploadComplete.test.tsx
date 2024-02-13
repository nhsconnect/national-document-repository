import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { render, screen } from '@testing-library/react';
import UploadSummary, { Props } from '../uploadSummary/UploadSummary';

jest.mock('../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as jest.Mock;
const mockPatient = buildPatientDetails();

describe('UploadSummary', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page', () => {
        renderUploadSummary({ documents: [] });

        expect(screen.getByRole('heading', { name: 'Upload Summary' })).toBeInTheDocument();
        expect(
            screen.getByRole('heading', {
                name: /All documents have been successfully uploaded on/,
            }),
        ).toBeInTheDocument();
        expect(screen.getByText('NHS Number')).toBeInTheDocument();
        expect(screen.getByText('Surname')).toBeInTheDocument();
        expect(screen.getByText('First name')).toBeInTheDocument();
        expect(screen.getByText('Date of birth')).toBeInTheDocument();
        expect(screen.getByText('Postcode')).toBeInTheDocument();
        expect(screen.getByText('Before you close this page')).toBeInTheDocument();
        expect(
            screen.queryByText('Some of your documents failed to upload'),
        ).not.toBeInTheDocument();
        expect(screen.queryByText('View successfully uploaded documents')).not.toBeInTheDocument();
    });
});

const renderUploadSummary = (propsOverride: Partial<Props>) => {
    const props: Props = {
        documents: [],
        ...propsOverride,
    };

    render(<UploadSummary {...props} />);
};
