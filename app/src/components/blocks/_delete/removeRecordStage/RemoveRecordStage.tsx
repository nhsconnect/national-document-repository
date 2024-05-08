import React, { Dispatch, SetStateAction } from 'react';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import useTitle from '../../../../helpers/hooks/useTitle';
import { BackLink, Button, Table, WarningCallout } from 'nhsuk-react-components';
import PatientDetails from '../../../generic/patientDetails/PatientDetails';
import moment, { Moment } from 'moment';
import LinkButton from '../../../generic/linkButton/LinkButton';

export type Props = {
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    recordType: string;
};

type DownloadDocument = {
    filename: string;
    uploaded: Moment;
};

function RemoveRecordStage({ setStage, recordType }: Props) {
    useTitle({ pageTitle: 'Remove record' });
    const nameTest = 'of4_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010]';
    const documents = Array.apply(null, Array(4)).map((x, i) => ({
        filename: i + 1 + nameTest,
        uploaded: moment(),
    }));

    return (
        <>
            <BackLink
                data-testid="back-link"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    setStage(LG_RECORD_STAGE.RECORD);
                }}
            >
                Go back
            </BackLink>
            <h1>Remove this {recordType}</h1>
            <WarningCallout>
                <WarningCallout.Label>Before removing</WarningCallout.Label>
                <p>
                    Only permanently remove this patient record if you have a valid reason to. For
                    example, you confirmed these files have reached the end of their retention
                    period.
                </p>
            </WarningCallout>
            <PatientDetails />
            {documents && documents.length > 0 && (
                <Table caption="List of files in record" id="current-documents-table">
                    <Table.Head>
                        <Table.Row>
                            <Table.Cell>Filename</Table.Cell>
                            <Table.Cell>Upload date</Table.Cell>
                        </Table.Row>
                    </Table.Head>

                    <Table.Body>
                        {documents.map(({ filename, uploaded }: DownloadDocument) => {
                            return (
                                <Table.Row key={filename}>
                                    <Table.Cell>
                                        <div>{filename}</div>
                                    </Table.Cell>
                                    <Table.Cell>{uploaded.format()}</Table.Cell>
                                </Table.Row>
                            );
                        })}
                    </Table.Body>
                </Table>
            )}
            <Button
                onClick={() => {
                    setStage(LG_RECORD_STAGE.DELETE_ALL);
                }}
            >
                Remove all files
            </Button>
            <LinkButton
                type="button"
                onClick={() => {
                    setStage(LG_RECORD_STAGE.RECORD);
                }}
            >
                Start again
            </LinkButton>
        </>
    );
}
export default RemoveRecordStage;
