import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
} from '../../types/pages/UploadDocumentsPage/types';
import { PatientDetails } from '../../types/generic/patientDetails';
import { SearchResult } from '../../types/generic/searchResult';
import { UserAuth } from '../../types/blocks/userAuth';
import { LloydGeorgeStitchResult } from '../requests/getLloydGeorgeRecord';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { v4 as uuidv4 } from 'uuid';
import moment from 'moment';
import { GlobalConfig, LocalFlags } from '../../providers/configProvider/ConfigProvider';
import { FeatureFlags } from '../../types/generic/featureFlags';
import { UploadSession } from '../../types/generic/uploadResult';

const buildUserAuth = (userAuthOverride?: Partial<UserAuth>) => {
    const auth: UserAuth = {
        role: REPOSITORY_ROLE.GP_ADMIN,
        isBSOL: false,
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
        active: true,
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

const buildLgFile = (
    fileNumber: number,
    numberOfFiles: number,
    patientname: string,
    size?: number,
    nhs_number: string = '9000000009',
    dob: string = '01-01-1970',
) => {
    const file = new File(
        ['test'],
        `${fileNumber}of${numberOfFiles}_Lloyd_George_Record_[${patientname}]_[${nhs_number}]_[${dob}].pdf`,
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
        id: uuidv4(),
        docType: docType ?? DOCUMENT_TYPE.ARF,
        attempts: 0,
    };
    return mockDocument;
};

const buildUploadSession = (documents: Array<UploadDocument>) => {
    return documents.reduce(
        (acc, doc) => ({
            ...acc,
            [doc.id]: {
                fields: {
                    key: `bucket/sub_folder/uuid_for_file(${doc.file.name})`,
                    'x-amz-algorithm': 'string',
                    'x-amz-credential': 'string',
                    'x-amz-date': 'string',
                    'x-amz-security-token': 'string',
                    policy: 'string',
                    'x-amz-signature': 'string',
                },
                url: 'https://test.s3.com',
            },
        }),
        {} as UploadSession,
    );
};

const buildSearchResult = (searchResultOverride?: Partial<SearchResult>) => {
    const result: SearchResult = {
        fileName: 'fileName.pdf',
        created: moment().format(),
        virusScannerResult: 'Clean',
        ID: '1234qwer-241ewewr',
        ...searchResultOverride,
    };
    return result;
};

const buildLgSearchResult = () => {
    const result: LloydGeorgeStitchResult = {
        jobStatus: 'Completed',
        numberOfFiles: 7,
        totalFileSizeInByte: 7,
        lastUpdated: '2023-10-03T09:11:54.618694Z',
        presignedUrl: 'https://test-url',
    };
    return result;
};

const buildConfig = (
    localFlagsOverride?: Partial<LocalFlags>,
    featureFlagsOverride?: Partial<FeatureFlags>,
) => {
    const globalConfig: GlobalConfig = {
        mockLocal: {
            isBsol: true,
            recordUploaded: true,
            userRole: REPOSITORY_ROLE.GP_ADMIN,
            ...localFlagsOverride,
        },
        featureFlags: {
            uploadLloydGeorgeWorkflowEnabled: false,
            uploadLambdaEnabled: false,
            uploadArfWorkflowEnabled: false,
            ...featureFlagsOverride,
        },
    };

    return globalConfig;
};

export {
    buildPatientDetails,
    buildTextFile,
    buildDocument,
    buildSearchResult,
    buildLgSearchResult,
    buildUserAuth,
    buildLgFile,
    buildConfig,
    buildUploadSession,
};
