import React, { Dispatch, SetStateAction } from 'react';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import useTitle from '../../../helpers/hooks/useTitle';

export type Props = {
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function RemoveRecordStage({ setStage }: Props) {
    useTitle({ pageTitle: 'Remove record' });

    return <div></div>;
}
export default RemoveRecordStage;
