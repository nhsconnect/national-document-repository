import { REPOSITORY_ROLE } from '../generic/authRole';
import {
    getRecordActionLinksAllowedForRole,
    PdfActionLink,
    RECORD_ACTION,
} from './lloydGeorgeActions';

describe('getAllowedRecordLinks', () => {
    describe('When role = GP_ADMIN, isBSOL = true', () => {
        it('returns record links for remove record and download record', () => {
            const role = REPOSITORY_ROLE.GP_ADMIN;
            const hasRecordInRepo = true;
            const expectedOutput = expect.arrayContaining([
                expect.objectContaining({
                    label: 'Remove files',
                    key: 'delete-all-files-link',
                    type: RECORD_ACTION.UPDATE,
                }),
                expect.objectContaining({
                    label: 'Download files',
                    key: 'download-all-files-link',
                    type: RECORD_ACTION.DOWNLOAD,
                }),
            ]);

            const actual = getRecordActionLinksAllowedForRole({ role, hasRecordInRepo });

            expect(actual).toEqual(expectedOutput);
        });
        it('returns an empty array if no record in repo (aka nothing to download or remove)', () => {
            const role = REPOSITORY_ROLE.GP_ADMIN;
            const hasRecordInRepo = false;
            const expectedOutput: Array<PdfActionLink> = [];
            const actual = getRecordActionLinksAllowedForRole({ role, hasRecordInRepo });

            expect(actual).toEqual(expectedOutput);
        });
    });

    describe('When role = GP_CLINICAL', () => {
        it('returns an empty array in any case', () => {
            const role = REPOSITORY_ROLE.GP_CLINICAL;

            expect(getRecordActionLinksAllowedForRole({ role, hasRecordInRepo: true })).toEqual([]);
            expect(getRecordActionLinksAllowedForRole({ role, hasRecordInRepo: false })).toEqual(
                [],
            );
        });
    });
});
