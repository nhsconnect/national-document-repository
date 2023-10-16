import React, { Dispatch, SetStateAction, useEffect } from 'react';
import getAllLloydGeorgePDFs from '../../../helpers/requests/getAllLloydGeorgePDFs';
import { Card } from 'nhsuk-react-components';
import { Link } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';

type Props = {
    numberOfFiles: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function LgDownloadAllStage({ numberOfFiles, setStage }: Props) {
    const progress = '47%';
    useEffect(() => {
        const onPageLoad = async () => {
            const response = await getAllLloydGeorgePDFs();
        };
        void onPageLoad();
    }, []);
    return (
        <>
            <h1>Downloading documents</h1>
            <h2 style={{ margin: 0 }}>Alex Cool Bloggs</h2>
            <h4 style={{ fontWeight: 'unset', fontStyle: 'unset' }}>NHS number: 1428571428</h4>
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
