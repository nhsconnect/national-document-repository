import React from 'react';
import { Card } from 'nhsuk-react-components';
import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import usePatient from '../../../helpers/hooks/usePatient';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
interface Props {
    documents: Array<UploadDocument>;
}

function LloydGeorgeUploadComplete({ documents }: Props) {
    // const navigate = useNavigate();
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber || '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);

    const successfulUploads = documents.filter((document) => {
        return document.state === DOCUMENT_UPLOAD_STATE.SUCCEEDED;
    });

    return (
        <div className="lg-upload-complete">
            <Card style={{ maxWidth: '620px' }} className="lg-upload-complete-card">
                <Card.Content>
                    <Card.Heading style={{ margin: 'auto' }}>Record uploaded for</Card.Heading>
                    <Card.Description style={{ fontWeight: '700', fontSize: '24px' }}>
                        {patientDetails?.givenName?.map((name) => `${name} `)}
                        {patientDetails?.familyName}
                    </Card.Description>
                    <Card.Description style={{ fontSize: '16px' }}>
                        NHS number: {formattedNhsNumber}
                    </Card.Description>
                    <Card.Description style={{ fontWeight: '700', fontSize: '24px' }}>
                        Date uploaded: {getFormattedDate(new Date())}
                    </Card.Description>
                </Card.Content>
            </Card>
            <p style={{ marginTop: 40 }}>
                You have successfully uploaded {successfulUploads.length} file
                {successfulUploads.length !== 1 && 's'}
            </p>
        </div>
    );
}

export default LloydGeorgeUploadComplete;
