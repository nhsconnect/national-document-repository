import axios from 'axios';
import {
    buildDocument,
    buildLgFile,
    buildUploadSession,
    buildPatientDetails,
} from '../test/testBuilders';
import {
    DOCUMENT_STATUS,
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
} from '../../types/pages/UploadDocumentsPage/types';
import { getDocumentStatus, uploadDocumentToS3, generateFileName } from './uploadDocuments';
import waitForSeconds from '../utils/waitForSeconds';
import { describe, expect, it, Mocked, vi } from 'vitest';
import { DocumentStatusResult } from '../../types/generic/uploadResult';
import { endpoints } from '../../types/generic/endpoints';
import { v4 as uuidv4 } from 'uuid';

vi.mock('axios');
vi.mock('../utils/waitForSeconds', () => ({
    default: vi.fn(),
}));

const mockedAxios = axios as Mocked<typeof axios>;
const mockedWaitForSeconds = waitForSeconds as Mocked<typeof waitForSeconds>;

const nhsNumber = '9000000009';
const baseUrl = 'http://localhost/test';
const baseHeaders = { 'Content-Type': 'application/json', test: 'test' };

describe('uploadDocumentToS3', () => {
    const testFile = buildLgFile(1);
    const testDocument = buildDocument(
        testFile,
        DOCUMENT_UPLOAD_STATE.SELECTED,
        DOCUMENT_TYPE.LLOYD_GEORGE,
    );
    const mockUploadSession = buildUploadSession([testDocument]);
    const mockSetDocuments = vi.fn();

    it('make POST request to s3 bucket', async () => {
        await uploadDocumentToS3({
            setDocuments: mockSetDocuments,
            uploadSession: mockUploadSession,
            document: testDocument,
        });

        expect(mockedAxios.post).toHaveBeenCalledTimes(1);
    });
});

describe('generateFileName', () => {
    it('generates correct filename with valid patient details', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['John', 'Michael'],
            familyName: 'Smith',
            nhsNumber: '1234567890',
            birthDate: '1990-05-15',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe(
            '1of1_Lloyd_George_Record_[John Michael SMITH]_[1234567890]_[15-05-1990].pdf',
        );
    });

    it('generates correct filename with single given name', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['Jane'],
            familyName: 'Doe',
            nhsNumber: '0987654321',
            birthDate: '1985-12-25',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe('1of1_Lloyd_George_Record_[Jane DOE]_[0987654321]_[25-12-1985].pdf');
    });

    it('handles special characters in given name by replacing them with dashes', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['Mary/Jane', "O'Connor"],
            familyName: 'Smith-Jones',
            nhsNumber: '1111222233',
            birthDate: '1975-03-10',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe(
            "1of1_Lloyd_George_Record_[Mary-Jane O'Connor SMITH-JONES]_[1111222233]_[10-03-1975].pdf",
        );
    });

    it('handles multiple special characters that need to be replaced', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['Test<Name>'],
            familyName: 'Sample*Family',
            nhsNumber: '5555666677',
            birthDate: '2000-01-01',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe(
            '1of1_Lloyd_George_Record_[Test-Name- SAMPLE*FAMILY]_[5555666677]_[01-01-2000].pdf',
        );
    });

    it('handles empty given name array', () => {
        const patientDetails = buildPatientDetails({
            givenName: [],
            familyName: 'OnlyFamily',
            nhsNumber: '9999888877',
            birthDate: '1965-07-20',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe('1of1_Lloyd_George_Record_[ ONLYFAMILY]_[9999888877]_[20-07-1965].pdf');
    });

    it('handles birth date with single digit day and month', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['Alex'],
            familyName: 'Wilson',
            nhsNumber: '1122334455',
            birthDate: '1992-02-05',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe('1of1_Lloyd_George_Record_[Alex WILSON]_[1122334455]_[05-02-1992].pdf');
    });

    it('throws an error when patient details is null', () => {
        expect(() => generateFileName(null)).toThrow(
            'Patient details are required to generate filename',
        );
    });

    it('handles all special characters that should be replaced', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['Test,Name/With\\Various?Characters%With*More:|"And<Finally>'],
            familyName: 'NormalFamily',
            nhsNumber: '1234567890',
            birthDate: '1980-06-15',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe(
            '1of1_Lloyd_George_Record_[Test-Name-With-Various-Characters-With-More---And-Finally- NORMALFAMILY]_[1234567890]_[15-06-1980].pdf',
        );
    });

    it('handles very long names correctly', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['Supercalifragilisticexpialidocious', 'AnExtremelyLongMiddleName'],
            familyName: 'AnExtremelyLongFamilyNameThatGoesOnAndOn',
            nhsNumber: '1111111111',
            birthDate: '1995-09-30',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe(
            '1of1_Lloyd_George_Record_[Supercalifragilisticexpialidocious AnExtremelyLongMiddleName ANEXTREMELYLONGFAMILYNAMETHATGOESONANDON]_[1111111111]_[30-09-1995].pdf',
        );
    });

    it('handles invalid birth date gracefully', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['Test'],
            familyName: 'User',
            nhsNumber: '1234567890',
            birthDate: 'invalid-date',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe('1of1_Lloyd_George_Record_[Test USER]_[1234567890]_[NaN-NaN-NaN].pdf');
    });

    it('handles whitespace in names correctly', () => {
        const patientDetails = buildPatientDetails({
            givenName: ['  John  ', '  Michael  '],
            familyName: '  Smith  ',
            nhsNumber: '1234567890',
            birthDate: '1990-01-01',
        });

        const result = generateFileName(patientDetails);

        expect(result).toBe(
            '1of1_Lloyd_George_Record_[  John     Michael     SMITH  ]_[1234567890]_[01-01-1990].pdf',
        );
    });
});

describe('getDocumentStatus', () => {
    it('should request document status for all documents provided', async () => {
        const documents = [
            buildDocument(
                buildLgFile(1),
                DOCUMENT_UPLOAD_STATE.UPLOADING,
                DOCUMENT_TYPE.LLOYD_GEORGE,
            ),
            buildDocument(
                buildLgFile(2),
                DOCUMENT_UPLOAD_STATE.UPLOADING,
                DOCUMENT_TYPE.LLOYD_GEORGE,
            ),
        ];

        const data: DocumentStatusResult = {};
        documents.forEach((doc) => {
            doc.ref = uuidv4();
            data[doc.ref] = {
                status: DOCUMENT_STATUS.FINAL,
            };
        });

        mockedAxios.get.mockResolvedValue({
            statusCode: 200,
            data,
        });

        const result = await getDocumentStatus({
            documents,
            baseUrl,
            baseHeaders,
            nhsNumber,
        });

        expect(mockedAxios.get).toHaveBeenCalledWith(baseUrl + endpoints.DOCUMENT_STATUS, {
            headers: baseHeaders,
            params: {
                patientId: nhsNumber,
                docIds: documents.map((d) => d.ref).join(','),
            },
        });
        expect(result).toBe(data);
    });
});
