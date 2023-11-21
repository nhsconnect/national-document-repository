import { render, screen, waitFor } from '@testing-library/react';
import LgRecordDetails, { Props } from './LloydGeorgeRecordDetails';
import { buildLgSearchResult } from '../../../helpers/test/testBuilders';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import * as ReactRouter from 'react-router';
import { createMemoryHistory } from 'history';
import userEvent from '@testing-library/user-event';
import { act } from 'react-dom/test-utils';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import useRole from '../../../helpers/hooks/useRole';
import { actionLinks } from '../../../types/blocks/lloydGeorgeActions';
jest.mock('../../../helpers/hooks/useRole');

const mockPdf = buildLgSearchResult();
const mockSetStaqe = jest.fn();
const mockedUseRole = useRole as jest.Mock;

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

        it('renders record details actions menu', async () => {
            renderComponent();

            expect(screen.getByText(`Select an action...`)).toBeInTheDocument();
            expect(screen.getByTestId('actions-menu')).toBeInTheDocument();
            actionLinks.forEach((action) => {
                expect(screen.queryByText(action.label)).not.toBeInTheDocument();
            });

            act(() => {
                userEvent.click(screen.getByTestId('actions-menu'));
            });
            await waitFor(async () => {
                actionLinks.forEach((action) => {
                    expect(screen.getByText(action.label)).toBeInTheDocument();
                });
            });
        });

        it.each(actionLinks)("renders actionLink '$label'", async (action) => {
            renderComponent();

            expect(screen.getByText(`Select an action...`)).toBeInTheDocument();
            expect(screen.getByTestId('actions-menu')).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByTestId('actions-menu'));
            });
            await waitFor(async () => {
                expect(screen.getByText(action.label)).toBeInTheDocument();
            });
        });
    });

    describe('Navigation', () => {
        it.each(actionLinks)(
            "navigates to '$stage' when action '$label' is clicked",
            async (action) => {
                renderComponent();

                expect(screen.getByText(`Select an action...`)).toBeInTheDocument();
                expect(screen.getByTestId('actions-menu')).toBeInTheDocument();

                act(() => {
                    userEvent.click(screen.getByTestId('actions-menu'));
                });
                await waitFor(async () => {
                    expect(screen.getByText(action.label)).toBeInTheDocument();
                });

                act(() => {
                    userEvent.click(screen.getByText(action.label));
                });
                await waitFor(async () => {
                    expect(mockSetStaqe).toHaveBeenCalledWith(action.stage);
                });
            },
        );
    });

    describe('Unauthorised', () => {
        const unauthorisedLinks = actionLinks.filter((a) => Array.isArray(a.unauthorised));

        it.each(unauthorisedLinks)(
            "does not render actionLink '$label' if role is unauthorised",
            async (action) => {
                const [unauthorisedRole] = action.unauthorised ?? [];
                mockedUseRole.mockReturnValue(unauthorisedRole);

                renderComponent();

                expect(screen.getByText(`Select an action...`)).toBeInTheDocument();
                expect(screen.getByTestId('actions-menu')).toBeInTheDocument();

                act(() => {
                    userEvent.click(screen.getByTestId('actions-menu'));
                });
                await waitFor(async () => {
                    expect(screen.queryByText(action.label)).not.toBeInTheDocument();
                });
            },
        );

        it.each(unauthorisedLinks)(
            "does not render actionLink '$label' for GP Clinical Role",
            async (action) => {
                expect(action.unauthorised).toContain(REPOSITORY_ROLE.GP_CLINICAL);
            },
        );
    });
});

const TestApp = (props: Omit<Props, 'setStage'>) => {
    const history = createMemoryHistory({
        initialEntries: ['/', '/example'],
        initialIndex: 1,
    });
    return (
        <ReactRouter.Router navigator={history} location={'/example'}>
            <LgRecordDetails {...props} setStage={mockSetStaqe} />;
        </ReactRouter.Router>
    );
};

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage' | 'stage'> = {
        lastUpdated: mockPdf.last_updated,
        numberOfFiles: mockPdf.number_of_files,
        totalFileSizeInByte: mockPdf.total_file_size_in_byte,

        ...propsOverride,
    };
    return render(<TestApp {...props} />);
};
