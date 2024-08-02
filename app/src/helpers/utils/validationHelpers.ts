import { UploadFilesErrors } from '../../types/pages/UploadDocumentsPage/types';

export function joinNumbersAsWords(numbers: number[]): string {
    const lastTwoNumbers = numbers.slice(-2);
    const others = numbers.slice(0, -2);
    const lastPart = lastTwoNumbers.join(' and ');
    return [...others, lastPart].join(', ');
}

export function fromOneToN(size: number): number[] {
    const result = [];
    for (let i = 1; i <= size; i++) {
        result.push(i);
    }
    return result;
}

export function countElements(array: number[]): Record<number, number> {
    const counter = {} as Record<number, number>;
    array.forEach((element) => {
        counter[element] = counter[element] ?? 0;
        counter[element] += 1;
    });
    return counter;
}

export function unique(array: UploadFilesErrors[]): UploadFilesErrors[] {
    const seen = new Set();
    const result: UploadFilesErrors[] = [];

    array.forEach((element) => {
        const errorJsonString = JSON.stringify(element);
        if (!seen.has(errorJsonString)) {
            result.push(element);
            seen.add(errorJsonString);
        }
    });

    return result;
}
