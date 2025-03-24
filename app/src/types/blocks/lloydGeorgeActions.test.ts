import { REPOSITORY_ROLE } from '../generic/authRole';
import { getUserRecordActionLinks, LGRecordActionLink, RECORD_ACTION } from './lloydGeorgeActions';

describe('getUserRecordActionLinks', () => {
    describe('When role = GP_ADMIN', () => {
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

            const actual = getUserRecordActionLinks({
                role,
                hasRecordInStorage: hasRecordInRepo,
            });

            expect(actual).toEqual(expectedOutput);
        });
        it('returns an empty array if no record in repo (aka nothing to download or remove)', () => {
            const role = REPOSITORY_ROLE.GP_ADMIN;
            const hasRecordInRepo = false;
            const expectedOutput: Array<LGRecordActionLink> = [];
            const actual = getUserRecordActionLinks({
                role,
                hasRecordInStorage: hasRecordInRepo,
            });

            expect(actual).toEqual(expectedOutput);
        });
    });

    describe('When role = GP_CLINICAL', () => {
        it('returns an empty array in any case', () => {
            const role = REPOSITORY_ROLE.GP_CLINICAL;

            expect(getUserRecordActionLinks({ role, hasRecordInStorage: true })).toEqual([]);
            expect(getUserRecordActionLinks({ role, hasRecordInStorage: false })).toEqual([]);
        });
    });
});
