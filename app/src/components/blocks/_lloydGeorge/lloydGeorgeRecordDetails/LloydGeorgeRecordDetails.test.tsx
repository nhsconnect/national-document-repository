import { render, screen } from '@testing-library/react';
import LgRecordDetails, { Props } from './LloydGeorgeRecordDetails';
import { buildLgSearchResult } from '../../../../helpers/test/testBuilders';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import useRole from '../../../../helpers/hooks/useRole';
import { lloydGeorgeRecordLinksInBSOL } from '../../../../types/blocks/lloydGeorgeActions';
import { LinkProps } from 'react-router-dom';
import useIsBSOL from '../../../../helpers/hooks/useIsBSOL';

jest.mock('../../../../helpers/hooks/useRole');
jest.mock('../../../../helpers/hooks/useIsBSOL');

const mockedUseNavigate = jest.fn();
const mockPdf = buildLgSearchResult();
const mockSetDownloadRemoveButtonClicked = jest.fn();
const mockSetError = jest.fn();
const mockSetFocus = jest.fn();
const mockedUseRole = useRole as jest.Mock;
const mockedUseIsBSOL = useIsBSOL as jest.Mock;

jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));

describe('LloydGeorgeRecordDetails', () => {
    beforeEach(() => {
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.PCSE);
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('Rendering', () => {
        it('renders the record details component', () => {
            renderComponent();

            expect(screen.getByText(`Last updated: ${mockPdf.last_updated}`)).toBeInTheDocument();
            expect(screen.getByText(`${mockPdf.number_of_files} files`)).toBeInTheDocument();
            expect(
                screen.getByText(`File size: ${formatFileSize(mockPdf.total_file_size_in_byte)}`),
            ).toBeInTheDocument();
            expect(screen.getByText('File format: PDF')).toBeInTheDocument();
        });
    });

    describe('Unauthorised', () => {
        const unauthorisedLinks = lloydGeorgeRecordLinksInBSOL.filter((a) =>
            Array.isArray(a.unauthorised),
        );

        it.each(unauthorisedLinks)(
            "does not render actionLink '$label' if role is unauthorised",
            async (action) => {
                const [unauthorisedRole] = action.unauthorised ?? [];
                mockedUseRole.mockReturnValue(unauthorisedRole);

                renderComponent();

                expect(screen.queryByText(`Select an action...`)).not.toBeInTheDocument();
                expect(screen.queryByTestId('actions-menu')).not.toBeInTheDocument();
            },
        );

        it.each(unauthorisedLinks)(
            "does not render actionLink '$label' for GP Clinical Role",
            async (action) => {
                expect(action.unauthorised).toContain(REPOSITORY_ROLE.GP_CLINICAL);
            },
        );
    });

    describe('GP admin non BSOL user', () => {
        it('renders the record details component', () => {
            mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
            mockedUseIsBSOL.mockReturnValue(false);
            renderComponent();

            expect(screen.getByText(`Last updated: ${mockPdf.last_updated}`)).toBeInTheDocument();
            expect(screen.getByText(`${mockPdf.number_of_files} files`)).toBeInTheDocument();
            expect(
                screen.getByText(`File size: ${formatFileSize(mockPdf.total_file_size_in_byte)}`),
            ).toBeInTheDocument();
            expect(screen.getByText('File format: PDF')).toBeInTheDocument();

            expect(screen.queryByText(`Select an action...`)).not.toBeInTheDocument();
            expect(screen.queryByTestId('actions-menu')).not.toBeInTheDocument();
        });
    });
});

type mockedProps = Omit<
    Props,
    'setStage' | 'stage' | 'setDownloadRemoveButtonClicked' | 'setError' | 'setFocus'
>;
const TestApp = (props: mockedProps) => {
    return (
        <LgRecordDetails
            {...props}
            setDownloadRemoveButtonClicked={mockSetDownloadRemoveButtonClicked}
            setError={mockSetError}
            setFocus={mockSetFocus}
        />
    );
};

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: mockedProps = {
        lastUpdated: mockPdf.last_updated,
        numberOfFiles: mockPdf.number_of_files,
        totalFileSizeInByte: mockPdf.total_file_size_in_byte,
        downloadRemoveButtonClicked: false,
        ...propsOverride,
    };
    return render(<TestApp {...props} />);
};
