import { getLastURLPath } from './urlManipulations';

describe('getLastURLPath', () => {
    it('return the last part of a url path', () => {
        const mockNormalUrl = 'https://localhost/a/fake/url/for/testing';
        const expected = 'testing';

        const actual = getLastURLPath(mockNormalUrl);
        expect(actual).toEqual(expected);
    });

    it('can handle s3 urls', () => {
        const mockS3Url = 's3://mock-bucket/subdir-1/subdir-2/test-uuid';
        const expected = 'test-uuid';

        const actual = getLastURLPath(mockS3Url);
        expect(actual).toEqual(expected);
    });
});
