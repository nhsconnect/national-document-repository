import { render } from '@testing-library/react';
import LgDownloadAllStage, { Props } from './LgDownloadAllStage';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { useState } from 'react';
import { buildLgSearchResult, buildPatientDetails } from '../../../helpers/test/testBuilders';
import { createMemoryHistory } from 'history';
import * as ReactRouter from 'react-router';
import SessionProvider from '../../../providers/sessionProvider/SessionProvider';
const mockPdf = buildLgSearchResult();
const mockPatient = buildPatientDetails();
describe('LgDownloadAllStage', () => {
    it('renders the component', () => {
        renderComponent();
    });
});

const TestApp = (props: Omit<Props, 'setStage'>) => {
    const [, setStage] = useState(LG_RECORD_STAGE.DOWNLOAD_ALL);
    const history = createMemoryHistory({
        initialEntries: ['/', '/example'],
        initialIndex: 1,
    });
    return (
        <SessionProvider>
            <ReactRouter.Router navigator={history} location={'/example'}>
                <LgDownloadAllStage {...props} setStage={setStage} />
            </ReactRouter.Router>
        </SessionProvider>
    );
};

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage'> = {
        numberOfFiles: mockPdf.number_of_files,
        patientDetails: mockPatient,
        ...propsOverride,
    };

    render(<TestApp {...props} />);
};
