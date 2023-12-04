const gpRoles = ['GP_ADMIN', 'GP_CLINICAL'];

describe('GP Workflow: Upload docs and verify', () => {
    gpRoles.forEach((role) => {
        it(`[Smoke] can navigate from Start page to Upload page as ${role}`, () => {});

        it(`[Smoke] can upload a single ARF or LG file, then renders 'Upload Summary' page for successful upload as ${role}`, () => {});
    });
});
