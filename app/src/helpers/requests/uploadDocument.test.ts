import axios from 'axios';
import { buildDocument, buildLgFile, buildUploadSession } from '../test/testBuilders';
import {
    DOCUMENT_STATUS,
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
} from '../../types/pages/UploadDocumentsPage/types';
import { getDocumentStatus, uploadDocumentToS3 } from './uploadDocuments';
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
