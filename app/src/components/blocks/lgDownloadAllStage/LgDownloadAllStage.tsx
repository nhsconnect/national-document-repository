import React, { Dispatch, SetStateAction, useEffect, useMemo, useRef, useState } from 'react';
import { Card } from 'nhsuk-react-components';
import { Link } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { useBaseAPIUrl } from '../../../providers/configProvider/ConfigProvider';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import getPresignedUrlForZip from '../../../helpers/requests/getPresignedUrlForZip';
import { DOCUMENT_TYPE } from '../../../types/pages/UploadDocumentsPage/types';

export type Props = {
    numberOfFiles: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    patientDetails: PatientDetails;
};

type DownloadLinkAttributes = {
    url: string;
    filename: string;
};

function LgDownloadAllStage({ numberOfFiles, setStage, patientDetails }: Props) {
    const timeToComplete = 600;
    const [progress, setProgress] = useState(0);
    var FakeProgress = require('../../../helpers/modules/fakeProgress');
    var p = useMemo(
        () =>
            new FakeProgress({
                timeConstant: timeToComplete,
                autoStart: true,
            }),
        [FakeProgress],
    );
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const [linkAttributes, setLinkAttributes] = useState<DownloadLinkAttributes>({
        url: '',
        filename: '',
    });
    const [triggerDownload, setTriggerDownload] = useState(false);
    const linkRef = useRef<HTMLAnchorElement | null>(null);
    const mounted = useRef(false);
    const triggered = useRef(false);

    const { nhsNumber } = patientDetails;

    useEffect(() => {
        if (linkRef.current && linkAttributes.url && triggerDownload) {
            linkRef.current.click();
        }
    }, [triggerDownload, linkAttributes]);

    useEffect(() => {
        let interval: number = 0;
        if (!progress) {
            interval = window.setInterval(() => {
                setProgress(parseInt((p.progress * 100).toFixed(1)));
            }, 200);
        } else if (progress >= 100) {
            setTriggerDownload(true);
            clearInterval(interval);
        }
    }, [baseHeaders, baseUrl, nhsNumber, p.progress, progress]);

    useEffect(() => {
        const onPageLoad = async () => {
            try {
                const preSignedUrl = await getPresignedUrlForZip({
                    baseUrl,
                    baseHeaders,
                    nhsNumber,
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                });

                const filename = `lloyd_george-patient-record-${nhsNumber}`;

                setLinkAttributes({ url: preSignedUrl, filename: filename });
            } catch (e) {}
            mounted.current = true;
        };

        if (!mounted.current && !triggered.current) {
            triggered.current = true;
            setTimeout(
                async () => {
                    const cachedProgress = p.progress;
                    p.stop();
                    await onPageLoad();
                    p.start(cachedProgress);
                },
                (timeToComplete / 2) * 3,
            );
        }
    }, [baseHeaders, baseUrl, nhsNumber, p]);

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
                            <span>{`${progress} %`} downloaded...</span>
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
