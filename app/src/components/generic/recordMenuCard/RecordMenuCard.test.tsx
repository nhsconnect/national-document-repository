import { act, render, screen } from '@testing-library/react';
import RecordMenuCard from './RecordMenuCard';
import useRole from '../../../helpers/hooks/useRole';
import { LGRecordActionLink, RECORD_ACTION } from '../../../types/blocks/lloydGeorgeActions';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { LinkProps } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import { routes } from '../../../types/generic/routes';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../helpers/hooks/useRole');
const mockSetStage = vi.fn();
const mockedUseNavigate = vi.fn();
const mockedUseRole = useRole as Mock;
const mockShowDownloadAndRemoveConfirmation = vi.fn();

const mockLinks: Array<LGRecordActionLink> = [
    {
        label: 'Upload files',
        key: 'upload-files-link',
        type: RECORD_ACTION.UPDATE,
        href: routes.HOME,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInStorage: false,
    },
    {
        label: 'Remove files',
        key: 'delete-all-files-link',
        type: RECORD_ACTION.UPDATE,
        stage: LG_RECORD_STAGE.DELETE_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInStorage: true,
    },
    {
        label: 'Download files',
        key: 'download-all-files-link',
        type: RECORD_ACTION.DOWNLOAD,
        stage: LG_RECORD_STAGE.DOWNLOAD_ALL,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInStorage: true,
    },
    {
        label: 'Download and remove files',
        key: 'download-and-remove-all-files-link',
        type: RECORD_ACTION.DOWNLOAD,
        unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        showIfRecordInStorage: true,
        onClick: mockShowDownloadAndRemoveConfirmation,
    },
];

vi.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockedUseNavigate,
}));

describe('RecordMenuCard', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockedUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders menu', () => {
            render(
                <RecordMenuCard setStage={mockSetStage} recordLinks={mockLinks} showMenu={true} />,
            );
            expect(screen.getByRole('link', { name: 'Remove files' })).toBeInTheDocument();
            expect(screen.getByRole('link', { name: 'Upload files' })).toBeInTheDocument();
            expect(screen.getByRole('link', { name: 'Download files' })).toBeInTheDocument();
        });

        it('does not render a sub-section if no record links were under that section', () => {
            const mockLinksUpdateOnly = mockLinks.filter(
                (link) => link.type === RECORD_ACTION.UPDATE,
            );

            const { rerender } = render(
                <RecordMenuCard
                    setStage={mockSetStage}
                    recordLinks={mockLinksUpdateOnly}
                    showMenu={true}
                />,
            );
            expect(screen.getByRole('link', { name: 'Upload files' })).toBeInTheDocument();
            expect(screen.getByRole('link', { name: 'Remove files' })).toBeInTheDocument();
            expect(screen.queryByRole('link', { name: 'Download files' })).not.toBeInTheDocument();

            const mockLinksDownloadOnly = mockLinks.filter(
                (link) => link.type === RECORD_ACTION.DOWNLOAD,
            );
            rerender(
                <RecordMenuCard
                    setStage={mockSetStage}
                    recordLinks={mockLinksDownloadOnly}
                    showMenu={true}
                />,
            );
            expect(screen.getByRole('link', { name: 'Download files' })).toBeInTheDocument();

            expect(screen.queryByRole('link', { name: 'Upload files' })).not.toBeInTheDocument();
            expect(screen.queryByRole('link', { name: 'Remove files' })).not.toBeInTheDocument();
        });

        it('does not render anything if the given record links array is empty', () => {
            const { container } = render(
                <RecordMenuCard setStage={mockSetStage} recordLinks={[]} showMenu={false} />,
            );
            expect(container).toBeEmptyDOMElement();
        });

        it('render menu item as a <button> if link item does not have stage or href', () => {
            render(
                <RecordMenuCard setStage={mockSetStage} recordLinks={mockLinks} showMenu={true} />,
            );
            expect(
                screen.getByRole('button', { name: 'Download and remove files' }),
            ).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Download and remove files' }));
            });

            expect(mockShowDownloadAndRemoveConfirmation).toBeCalledTimes(1);
        });

        it('Does not render the MenuCard if showMenu is false', () => {
            const { container } = render(
                <RecordMenuCard setStage={mockSetStage} recordLinks={mockLinks} showMenu={false} />,
            );
            expect(container).toBeEmptyDOMElement();
        });
    });

    describe('Navigation', () => {
        it('navigates to href when clicked', () => {
            render(
                <RecordMenuCard setStage={mockSetStage} recordLinks={mockLinks} showMenu={true} />,
            );
            expect(screen.getByRole('link', { name: 'Upload files' })).toBeInTheDocument();
            act(() => {
                userEvent.click(screen.getByRole('link', { name: 'Upload files' }));
            });
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
        });

        it('change stage when clicked', () => {
            render(
                <RecordMenuCard setStage={mockSetStage} recordLinks={mockLinks} showMenu={true} />,
            );
            expect(screen.getByRole('link', { name: 'Remove files' })).toBeInTheDocument();

            act(() => {
                userEvent.click(screen.getByRole('link', { name: 'Remove files' }));
            });
            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.DELETE_ALL);
        });
    });
});
