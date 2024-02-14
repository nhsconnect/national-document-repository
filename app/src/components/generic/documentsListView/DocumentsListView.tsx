import { UploadDocument } from '../../../types/pages/UploadDocumentsPage/types';
import { Details } from 'nhsuk-react-components';
import React, { useState } from 'react';

interface Props {
    documentsList: Array<UploadDocument>;
    ariaLabel: string;
}

const DocumentsListView = ({ documentsList, ariaLabel }: Props) => {
    const [isExpanded, setIsExpanded] = useState(true);

    return (
        <Details open>
            <Details.Summary aria-label={ariaLabel} onClick={() => setIsExpanded(!isExpanded)}>
                {isExpanded ? 'Hide files' : 'View files'}
            </Details.Summary>
            <Details.Text>
                <ul className="document-list-view-list">
                    {documentsList.map((document) => {
                        return <li key={document.id}>{document.file.name}</li>;
                    })}
                </ul>
            </Details.Text>
        </Details>
    );
};

export default DocumentsListView;
