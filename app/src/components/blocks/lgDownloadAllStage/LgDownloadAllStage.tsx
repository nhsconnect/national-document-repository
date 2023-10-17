import React, { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import getAllLloydGeorgePDFs from '../../../helpers/requests/getAllLloydGeorgePDFs';
import { Card } from 'nhsuk-react-components';
import { Link } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { useBaseAPIUrl } from '../../../providers/configProvider/ConfigProvider';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';

type Props = {
    numberOfFiles: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    patientDetails: PatientDetails;
};

type DownloadLinkAttributes = {
    url: string;
    filename: string;
};

function LgDownloadAllStage({ numberOfFiles, setStage, patientDetails }: Props) {
    const [progress, setProgress] = useState(0);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const [linkAttributes, setLinkAttributes] = useState<DownloadLinkAttributes>({
        url: '',
        filename: '',
    });
    const linkRef = useRef<HTMLAnchorElement | null>(null);

    const { nhsNumber } = patientDetails;

    useEffect(() => {
        if (linkRef.current && linkAttributes.url) {
            setProgress(100);
            linkRef.current.click();
        }
    }, [linkAttributes]);

    useEffect(() => {
        setProgress(20);
        const onPageLoad = async () => {
            setProgress(40);

            const { presign_url } = await getAllLloydGeorgePDFs({
                baseUrl,
                baseHeaders,
                nhsNumber,
            });
            setProgress(80);

            const filename = `lloyd_george-patient-record-${nhsNumber}`;

            setLinkAttributes({ url: presign_url, filename: filename });
        };
        void onPageLoad();
    }, [baseHeaders, baseUrl, nhsNumber]);

    return (
        <>
            <h1>Downloading documents</h1>
            <h2 style={{ margin: 0 }}>
                {patientDetails.givenName + ' ' + patientDetails.familyName}
            </h2>
            <h4 style={{ fontWeight: 'unset', fontStyle: 'unset' }}>
                NHS number: {patientDetails.nhsNumber}
            </h4>
            <div className="nhsuk-heading-xl" />
            <h4 style={{ fontWeight: 'unset', fontStyle: 'unset' }}>
                Preparing download for {numberOfFiles} files
            </h4>

            <Card>
                <Card.Content>
                    <strong>
                        <p>Compressing record into a zip file</p>
                    </strong>

                    <div
                        style={{
                            display: 'flex',
                            flexFlow: 'row nowrap',
                            justifyContent: 'space-between',
                        }}
                    >
                        <div>
                            <span>{progress} downloaded...</span>
                            <a
                                hidden
                                id="download-link"
                                ref={linkRef}
                                href={linkAttributes.url}
                                download={linkAttributes.filename}
                            >
                                Download Lloyd George Documents URL
                            </a>
                        </div>
                        <div>
                            <Link
                                to="#"
                                onClick={(e) => {
                                    e.preventDefault();
                                    const w = global.window;
                                    if (
                                        typeof w !== 'undefined' &&
                                        w.confirm(
                                            'Are you sure you would like to cancel the download?',
                                        )
                                    ) {
                                        setStage(LG_RECORD_STAGE.RECORD);
                                    }
                                }}
                            >
                                Cancel
                            </Link>
                        </div>
                    </div>
                </Card.Content>
            </Card>
        </>
    );
}

export default LgDownloadAllStage;
