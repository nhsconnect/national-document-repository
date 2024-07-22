export function joinNumbersAsWords(numbers: number[]): string {
    const lastTwoNumbers = numbers.slice(-2);
    const others = numbers.slice(0, -2);
    const lastPart = lastTwoNumbers.join(' and ');
    return [...others, lastPart].join(', ');
}
