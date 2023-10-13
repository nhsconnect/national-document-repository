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
            <div>
                <h1>Downloading documents</h1>
                <br />
                <h2>Alex Cool Bloggs</h2>
                <h3>NHS number: 1428571428</h3>
            </div>
            <div>
                <span>Preparing download for {numberOfFiles} files</span>
            </div>
            <Card>
                <Card.Content>
                    <span style={{ fontStyle: 'strong' }}>Compressing record into a zip file</span>
                    <div>
                        <span>{progress} downloaded...</span>
                    </div>
                    <div
                        style={{
                            display: 'flex',
                            flexFlow: 'row nowrap',
                            justifyContent: 'space-between',
                        }}
                    >
                        <Link
                            to="#"
                            onClick={(e) => {
                                e.preventDefault();
                                setStage(LG_RECORD_STAGE.RECORD);
                            }}
                        >
                            Cancel
                        </Link>
                    </div>
                </Card.Content>
            </Card>
        </>
    );
}

export default LgDownloadAllStage;
