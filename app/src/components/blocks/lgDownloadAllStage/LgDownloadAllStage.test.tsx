import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import LgDownloadAllStage, { Props } from './LgDownloadAllStage';

describe('LgDownloadAllStage', () => {
    it('renders the component', () => {});
});

const renderComponent = (propsOverride: Partial<Props>) => {
    const props: Omit<Props, 'setStage'> = {
        numberOfFiles: 0,
        patientDetails: buildPatientDetails(),
        ...propsOverride,
    };
    render(<LgDownloadAllStage {...props} />);
};
