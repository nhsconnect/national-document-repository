require('dotenv').config();
console.log('checking envs...');

if ('VITE_DOC_STORE_API_ENDPOINT' in import.meta.env) {
    console.log('VITE_DOC_STORE_API_ENDPOINT is set');
} else {
    console.log('VITE_DOC_STORE_API_ENDPOINT not set');
}

if ('VITE_AWS_REGION' in import.meta.env) {
    console.log('VITE_AWS_REGION is set');
} else {
    console.log('VITE_AWS_REGION not set');
}

if ('VITE_OIDC_PROVIDER_ID' in import.meta.env) {
    console.log('VITE_OIDC_PROVIDER_ID is set');
} else {
    console.log('VITE_OIDC_PROVIDER_ID not set');
}

if ('VITE_IDENTITY_PROVIDER_POOL_ID' in import.meta.env) {
    console.log('VITE_IDENTITY_PROVIDER_POOL_ID is set');
} else {
    console.log('VITE_IDENTITY_PROVIDER_POOL_ID not set');
}

if ('VITE_MONITOR_ACCOUNT_ID' in import.meta.env) {
    console.log('VITE_MONITOR_ACCOUNT_ID is set');
} else {
    console.log('VITE_MONITOR_ACCOUNT_ID not set');
}

if ('VITE_ENVIRONMENT' in import.meta.env) {
    console.log('VITE_ENVIRONMENT is set');
} else {
    console.log('VITE_ENVIRONMENT not set');
}

if ('VITE_IMAGE_VERSION' in import.meta.env) {
    console.log('VITE_IMAGE_VERSION is set');
} else {
    console.log('VITE_IMAGE_VERSION not set');
}
