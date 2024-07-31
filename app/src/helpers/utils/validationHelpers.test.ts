import { countElements, fromOneToN, joinNumbersAsWords, unique } from './validationHelpers';
import { UPLOAD_FILE_ERROR_TYPE } from './fileUploadErrorMessages';

describe('joinNumbersAsWords', () => {
    const testCases = [
        { inputNumbers: [], expected: '' },
        { inputNumbers: [1], expected: '1' },
        { inputNumbers: [2, 3], expected: '2 and 3' },
        { inputNumbers: [1, 2, 3], expected: '1, 2 and 3' },
        { inputNumbers: [12, 345, 67, 89], expected: '12, 345, 67 and 89' },
        { inputNumbers: [135, 79, 24, 6, 8, 0], expected: '135, 79, 24, 6, 8 and 0' },
    ];

    it.each(testCases)(
        'take a list of numbers and output them in the format "a, b and c"',
        ({ inputNumbers, expected }) => {
            const actual = joinNumbersAsWords(inputNumbers);

            expect(actual).toEqual(expected);
        },
    );
});

describe('fromOneToN', () => {
    const testCases = [
        { size: 1, expected: [1] },
        { size: 2, expected: [1, 2] },
        { size: 5, expected: [1, 2, 3, 4, 5] },
        { size: 0, expected: [] },
        { size: -10, expected: [] },
        { size: 11, expected: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] },
    ];

    it.each(testCases)(
        'take an integer n and return an array of integers 1 to n',
        ({ size, expected }) => {
            const actual = fromOneToN(size);

            expect(actual).toEqual(expected);
        },
    );
});

describe('countElements', () => {
    const testCases = [
        { array: [1], expected: { 1: 1 } },
        { array: [1, 2, 3, 2, 3, 1, 1, 4, 0], expected: { 0: 1, 1: 3, 2: 2, 3: 2, 4: 1 } },
        { array: [12, 345, 6789, 12, 345, 12, 12], expected: { 12: 4, 345: 2, 6789: 1 } },
        { array: [], expected: {} },
    ];

    it.each(testCases)(
        'takes an array and return an object that counts the occurrence of each element in array',
        ({ array, expected }) => {
            const actual = countElements(array);

            expect(actual).toEqual(expected);
        },
    );
});

describe('unique', () => {
    it('take an UploadFilesErrors array and return it with duplicated elements removed', () => {
        const inputErrors = [
            {
                filename: '1of3_Lloyd_George_Record_[Jane Smith]_[9000000009]_[01-01-1970].pdf',
                error: UPLOAD_FILE_ERROR_TYPE.duplicateFile,
            },
            {
                filename: '2of3_Lloyd_George_Record_[Bob Doe]_[9000000009]_[01-01-1970].pdf',
                error: UPLOAD_FILE_ERROR_TYPE.patientNameError,
            },
            {
                filename: '1of3_Lloyd_George_Record_[Jane Smith]_[9000000009]_[01-01-1970].pdf',
                error: UPLOAD_FILE_ERROR_TYPE.duplicateFile,
            },
        ];
        const expected = [
            {
                filename: '1of3_Lloyd_George_Record_[Jane Smith]_[9000000009]_[01-01-1970].pdf',
                error: UPLOAD_FILE_ERROR_TYPE.duplicateFile,
            },
            {
                filename: '2of3_Lloyd_George_Record_[Bob Doe]_[9000000009]_[01-01-1970].pdf',
                error: UPLOAD_FILE_ERROR_TYPE.patientNameError,
            },
        ];

        const actual = unique(inputErrors);

        expect(actual).toEqual(expected);
    });
});
