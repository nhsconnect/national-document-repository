import dotenv from 'dotenv';
dotenv.config();

console.log('checking envs...');

if (process.env.VITE_APP_DOC_STORE_API_ENDPOINT) {
    console.log('VITE_APP_DOC_STORE_API_ENDPOINT is set');
} else {
    console.log('VITE_APP_DOC_STORE_API_ENDPOINT not set');
}

if (process.env.VITE_APP_AWS_REGION) {
    console.log('VITE_APP_AWS_REGION is set');
} else {
    console.log('VITE_APP_AWS_REGION not set');
}

if (process.env.VITE_APP_OIDC_PROVIDER_ID) {
    console.log('VITE_APP_OIDC_PROVIDER_ID is set');
} else {
    console.log('VITE_APP_OIDC_PROVIDER_ID not set');
}

if (process.env.VITE_APP_ENVIRONMENT) {
    console.log('VITE_APP_ENVIRONMENT is set');
} else {
    console.log('VITE_APP_ENVIRONMENT not set');
}

if (process.env.VITE_APP_IMAGE_VERSION) {
    console.log('VITE_APP_IMAGE_VERSION is set');
} else {
    console.log('VITE_APP_IMAGE_VERSION not set');
}
