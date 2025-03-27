import waitForSeconds from './waitForSeconds';
import sinon, { SinonFakeTimers } from 'sinon';

describe('waitForSeconds', () => {
    let clock: SinonFakeTimers;

    beforeEach(() => {
        clock = sinon.useFakeTimers();
    });

    afterEach(() => {
        clock.restore();
    });

    it('postpone code execution by given number of seconds', async () => {
        const mockFunction = jest.fn();
        const secondsToWait = 2;
        const testCode = async () => {
            await waitForSeconds(secondsToWait);
            mockFunction(Date.now());
        };

        const startTime = Date.now();
        const promise = testCode();

        clock.tick(secondsToWait * 1000);
        await promise;

        expect(mockFunction).toHaveBeenCalledTimes(1);

        const timestampWhenMockFunctionCalled = mockFunction.mock.calls[0][0];
        expect(timestampWhenMockFunctionCalled).toBeGreaterThanOrEqual(
            startTime + 1000 * secondsToWait,
        );
        expect(timestampWhenMockFunctionCalled).toBeLessThanOrEqual(
            startTime + 1000 * (secondsToWait + 1),
        );
    });
});
