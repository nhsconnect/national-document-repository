const config = {
    Auth: {
        region: "eu-west-2",
        providerId: "%oidc-provider-id%",
    },
    API: {
        endpoints: [
            {
                name: "doc-store-api",
<<<<<<< HEAD
                endpoint: "https://wfsosmq04m.execute-api.eu-west-2.amazonaws.com/dev"
||||||| parent of 6f58e3f ([PRMDR-112] Change endpoint in config.js to sandbox b)
                endpoint: "https://y98819ugm5.execute-api.eu-west-2.amazonaws.com/prod"
=======
                endpoint: "https://y98819ugm5.execute-api.eu-west-2.amazonaws.com/dev"
>>>>>>> 6f58e3f ([PRMDR-112] Change endpoint in config.js to sandbox b)
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