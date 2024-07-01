export function getLastURLPath(url: string) {
    return url.split('/').at(-1);
}
