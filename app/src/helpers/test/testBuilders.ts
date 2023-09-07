import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
} from '../../types/pages/UploadDocumentsPage/types';
import { PatientDetails } from '../../types/generic/patientDetails';
import { SearchResult } from '../../types/generic/searchResult';

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

const buildDocument = (file: File, uploadStatus: DOCUMENT_UPLOAD_STATE) => {
    const mockDocument: UploadDocument = {
        file,
        state: uploadStatus ?? documentUploadStates.SUCCEEDED,
        progress: 0,
        id: Math.floor(Math.random() * 1000000).toString(),
    };
    return mockDocument;
};

const buildSearchResult = (searchResultOverride?: Partial<SearchResult>) => {
    const result: SearchResult = {
        id: 'some-id',
        description: 'Some description',
        type: 'some type',
        indexed: new Date(Date.UTC(2022, 7, 10, 10, 34, 41, 515)),
        virusScanResult: 'Clean',
        ...searchResultOverride,
    };
    return result;
};

export { buildPatientDetails, buildTextFile, buildDocument, buildSearchResult };
