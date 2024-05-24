export function getLastURLPath(url: string) {
    const splitUrl = url.split('/');
    const lastPartIndex = splitUrl.length - 1;
    return splitUrl[lastPartIndex];
}
