import waitForSeconds from './waitForSeconds';

describe('waitForSeconds', () => {
    it('postpone code execution by given number of seconds', async () => {
        const mockFunction = jest.fn();
        const secondsToWait = 2;
        const testCode = async () => {
            await waitForSeconds(secondsToWait);
            mockFunction(Date.now());
        };

        const startTime = Date.now();
        await testCode();

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
