import { joinNumbersAsWords } from './stringManipulations';

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
