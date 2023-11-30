function useBaseAPIUrl() {
    const apiEndpoint: string | undefined = process.env.REACT_APP_DOC_STORE_API_ENDPOINT;

    if (!apiEndpoint) {
        throw Error(`Document Store endpoint has not been set!`);
    }

    return apiEndpoint;
}

export default useBaseAPIUrl;
