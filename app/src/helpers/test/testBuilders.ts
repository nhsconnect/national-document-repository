import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
} from '../../types/pages/UploadDocumentsPage/types';
import { PatientDetails } from '../../types/generic/patientDetails';
import { SearchResult } from '../../types/generic/searchResult';
import { UserAuth } from '../../types/blocks/userAuth';

const buildUserAuth = (userAuthOverride?: Partial<UserAuth>) => {
    const auth: UserAuth = {
        organisations: [
            {
                org_name: 'PORTWAY LIFESTYLE CENTRE',
                ods_code: 'A470',
                role: 'DEV',
            },
        ],
        authorisation_token: '111xxx222',
        ...userAuthOverride,
    };
    return auth;
};

const buildPatientDetails = (patientDetailsOverride?: Partial<PatientDetails>) => {
    const patient: PatientDetails = {
        birthDate: '1970-01-01',
        familyName: 'Doe',
        givenName: ['John'],
        nhsNumber: '9000000009',
        postalCode: 'BS3 3NQ',
        superseded: false,
        restricted: false,
        ...patientDetailsOverride,
    };

    return patient;
};

const buildTextFile = (name: string, size?: number) => {
    const file = new File(['test'], `${name}.txt`, {
        type: 'text/plain',
    });

    if (size) {
        Object.defineProperty(file, 'size', {
            value: size,
        });
    }

    return file;
};

const buildLgFile = (name: number, numberOfFiles: number, size?: number) => {
    const file = new File(
        ['test'],
        `${name}of${numberOfFiles}_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf`,
        {
            type: 'application/pdf',
        },
    );

    if (size) {
        Object.defineProperty(file, 'size', {
            value: size,
        });
    }

    return file;
};

const buildDocument = (
    file: File,
    uploadStatus: DOCUMENT_UPLOAD_STATE,
    docType?: DOCUMENT_TYPE,
) => {
    const mockDocument: UploadDocument = {
        file,
        state: uploadStatus ?? documentUploadStates.SUCCEEDED,
        progress: 0,
        id: Math.floor(Math.random() * 1000000).toString(),
        docType: docType ?? DOCUMENT_TYPE.ARF,
    };
    return mockDocument;
};

const buildSearchResult = (searchResultOverride?: Partial<SearchResult>) => {
    const result: SearchResult = {
        fileName: 'Some description',
        created: '2023-09-06T10:41:51.899908Z',
        virusScannerResult: 'Clean',
        ...searchResultOverride,
    };
    return result;
};

export {
    buildUserAuth,
    buildPatientDetails,
    buildTextFile,
    buildDocument,
    buildSearchResult,
    buildLgFile,
};
