import { FieldValues, useForm } from 'react-hook-form';
import {
    DOCUMENT_TYPE,
    SetUploadDocuments,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { useNavigate } from 'react-router';
import { routes } from '../../../../types/generic/routes';
import { Button, Fieldset, Radios } from 'nhsuk-react-components';
import { useState } from 'react';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import useTitle from '../../../../helpers/hooks/useTitle';

type Props = {
    documents: UploadDocument[];
    setDocuments: SetUploadDocuments;
    documentType: DOCUMENT_TYPE;
};

enum REMOVE_DOCUMENTS_OPTION {
    YES = 'yes',
    NO = 'no',
}

const DocumentUploadRemoveFilesStage = ({ documents, setDocuments, documentType }: Props) => {
    const { register, handleSubmit } = useForm();
    const { ref: removeDocsRef, ...radioProps } = register('removeDocs');
    const [showNoOptionSelectedMessage, setShowNoOptionSelectedMessage] = useState<boolean>(false);
    const noOptionSelectedError = 'Select an option';

    const navigate = useNavigate();

    const confirmRemove = (fieldValues: FieldValues) => {
        if (fieldValues.removeDocs === REMOVE_DOCUMENTS_OPTION.YES) {
            setDocuments(documents.filter((doc) => doc.docType !== documentType));
            navigate(routes.DOCUMENT_UPLOAD);
        } else if (fieldValues.removeDocs === REMOVE_DOCUMENTS_OPTION.NO) {
            navigate(-1);
        } else {
            setShowNoOptionSelectedMessage(true);
        }
    };

    const pageTitle = 'Are you sure you want to remove all selected files?';
    useTitle({ pageTitle });

    return (
        <>
            {showNoOptionSelectedMessage && (
                <ErrorBox
                    messageTitle={'There is a problem '}
                    messageLinkBody={'You must select an option'}
                    errorBoxSummaryId={'error-box-summary'}
                    errorInputLink={'#remove-docs'}
                    dataTestId={'remove-error-box'}
                />
            )}
            <form onSubmit={handleSubmit(confirmRemove)}>
                <Fieldset>
                    <Fieldset.Legend isPageHeading>{pageTitle}</Fieldset.Legend>
                    <Radios
                        id="remove-documents"
                        error={showNoOptionSelectedMessage && noOptionSelectedError}
                    >
                        <Radios.Radio
                            value={REMOVE_DOCUMENTS_OPTION.YES}
                            inputRef={removeDocsRef}
                            {...radioProps}
                            id="yes-radio-button"
                            data-testid="yes-radio-btn"
                        >
                            Yes
                        </Radios.Radio>
                        <Radios.Radio
                            value={REMOVE_DOCUMENTS_OPTION.NO}
                            inputRef={removeDocsRef}
                            {...radioProps}
                            id="no-radio-button"
                            data-testid="no-radio-btn"
                        >
                            No
                        </Radios.Radio>
                    </Radios>
                </Fieldset>

                <Button type="submit" id="remove-submit-button" data-testid="remove-submit-btn">
                    Continue
                </Button>
            </form>
        </>
    );
};

export default DocumentUploadRemoveFilesStage;
