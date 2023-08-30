const config = {
    Auth: {
        region: "eu-west-2",
        providerId: "%oidc-provider-id%",
    },
    API: {
        endpoints: [
            {
                name: "doc-store-api",
                endpoint: "https://87gdl95l58.execute-api.eu-west-2.amazonaws.com/dev"
            },
        ],
    },
    features: {
        local: {
            OIDC_AUTHENTICATION: false,
        },
        dev: {
            OIDC_AUTHENTICATION: false,
        }
    }
};

export default config;