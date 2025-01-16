import formatFileSize from "./formatFileSize";

describe('formatFileSize', () => {

    it('returns rounded file size formats for valid inputs', () => {

        expect(formatFileSize(0)).toBe('0 bytes');
        expect(formatFileSize(-0)).toBe('0 bytes');
        expect(formatFileSize(1)).toBe('1 bytes');
        expect(formatFileSize(1.5)).toBe('2 bytes');

        expect(formatFileSize(1023)).toBe('1023 bytes');
        expect(formatFileSize(1024)).toBe('1 KB');
        expect(formatFileSize(1025)).toBe('1 KB');

        expect(formatFileSize(1535)).toBe('1 KB');
        expect(formatFileSize(1536)).toBe('2 KB');
        expect(formatFileSize(2048)).toBe('2 KB');

        expect(formatFileSize(Math.pow(2, 20) - 1)).toBe('1024 KB');
        expect(formatFileSize(Math.pow(2, 20))).toBe('1 MB');
        expect(formatFileSize(Math.pow(2, 20) + 1)).toBe('1 MB');

        expect(formatFileSize(Math.pow(2, 30) - 1)).toBe('1024 MB');
        expect(formatFileSize(Math.pow(2, 30))).toBe('1 GB');
        expect(formatFileSize(Math.pow(2, 30) + 1)).toBe('1 GB');

    });

    it('throws "Invalid file size" exception for invalid inputs', () => {

        expect(() => formatFileSize(Number.MIN_SAFE_INTEGER)).toThrow('Invalid file size');
        expect(() => formatFileSize(-1)).toThrow('Invalid file size');
        expect(() => formatFileSize(NaN)).toThrow('Invalid file size');
        expect(() => formatFileSize(undefined as unknown as number)).toThrow('Invalid file size');
        expect(() => formatFileSize(Math.pow(2, 40))).toThrow('Invalid file size');      // 1TB
        expect(() => formatFileSize(Number.MAX_SAFE_INTEGER)).toThrow('Invalid file size');

    });

});