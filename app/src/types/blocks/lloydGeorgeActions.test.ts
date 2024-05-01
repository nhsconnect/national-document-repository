import { REPOSITORY_ROLE } from '../generic/authRole';
import {
    getBSOLUserRecordActionLinks,
    getNonBSOLUserRecordActionLinks,
    LGRecordActionLink,
    RECORD_ACTION,
} from './lloydGeorgeActions';

describe('getBSOLUserRecordActionLinks', () => {
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

            const actual = getBSOLUserRecordActionLinks({
                role,
                hasRecordInStorage: hasRecordInRepo,
            });

            expect(actual).toEqual(expectedOutput);
        });
        it('returns an empty array if no record in repo (aka nothing to download or remove)', () => {
            const role = REPOSITORY_ROLE.GP_ADMIN;
            const hasRecordInRepo = false;
            const expectedOutput: Array<LGRecordActionLink> = [];
            const actual = getBSOLUserRecordActionLinks({
                role,
                hasRecordInStorage: hasRecordInRepo,
            });

            expect(actual).toEqual(expectedOutput);
        });
    });

    describe('When role = GP_CLINICAL', () => {
        it('returns an empty array in any case', () => {
            const role = REPOSITORY_ROLE.GP_CLINICAL;

            expect(getBSOLUserRecordActionLinks({ role, hasRecordInStorage: true })).toEqual([]);
            expect(getBSOLUserRecordActionLinks({ role, hasRecordInStorage: false })).toEqual([]);
        });
    });
});

describe('getNonBSOLUserRecordActionLinks', () => {
    const mockDownloadAndRemoveOnClick = jest.fn();
    describe('When role = GP_ADMIN', () => {
        it('returns record links for "download and remove"', () => {
            const role = REPOSITORY_ROLE.GP_ADMIN;
            const hasRecordInRepo = true;
            const expectedOutput = expect.arrayContaining([
                expect.objectContaining({
                    label: 'Download and remove files',
                    key: 'download-and-remove-record-btn',
                    type: RECORD_ACTION.DOWNLOAD,
                    onClick: mockDownloadAndRemoveOnClick,
                }),
            ]);

            const actual = getNonBSOLUserRecordActionLinks({
                role,
                hasRecordInStorage: hasRecordInRepo,
                onClickFunctionForDownloadAndRemove: mockDownloadAndRemoveOnClick,
            });

            expect(actual).toEqual(expectedOutput);
        });

        it('returns an empty array if no record in repo (aka nothing to download or remove)', () => {
            const role = REPOSITORY_ROLE.GP_ADMIN;
            const hasRecordInRepo = false;
            const expectedOutput: Array<LGRecordActionLink> = [];
            const actual = getNonBSOLUserRecordActionLinks({
                role,
                hasRecordInStorage: hasRecordInRepo,
                onClickFunctionForDownloadAndRemove: mockDownloadAndRemoveOnClick,
            });

            expect(actual).toEqual(expectedOutput);
        });
    });

    describe('When role = GP_CLINICAL', () => {
        const args = {
            role: REPOSITORY_ROLE.GP_CLINICAL,
            onClickFunctionForDownloadAndRemove: mockDownloadAndRemoveOnClick,
        };
        it('returns an empty array in any case', () => {
            const role = REPOSITORY_ROLE.GP_CLINICAL;

            expect(getNonBSOLUserRecordActionLinks({ ...args, hasRecordInStorage: true })).toEqual(
                [],
            );
            expect(
                getNonBSOLUserRecordActionLinks({
                    ...args,
                    hasRecordInStorage: false,
                }),
            ).toEqual([]);
        });
    });
});
