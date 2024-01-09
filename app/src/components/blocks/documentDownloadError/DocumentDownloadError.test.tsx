import { act, render, screen } from '@testing-library/react';
import LloydGeorgeRecordError from './DocumentDownloadError';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import { LinkProps } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import useRole from '../../../helpers/hooks/useRole';

const mockSetStage = jest.fn();
const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));

jest.mock('../../../helpers/hooks/useRole');
const mockUseRole = useRole as jest.Mock;

describe('LloydGeorgeRecordError', () => {
});
