require('dotenv').config();
console.log('checking envs...');

if ('REACT_APP_DOC_STORE_API_ENDPOINT' in process.env) {
    console.log('REACT_APP_DOC_STORE_API_ENDPOINT is set');
} else {
    console.log('REACT_APP_DOC_STORE_API_ENDPOINT not set');
}

if ('REACT_APP_AWS_REGION' in process.env) {
    console.log('REACT_APP_AWS_REGION is set');
} else {
    console.log('REACT_APP_AWS_REGION not set');
}

if ('REACT_APP_OIDC_PROVIDER_ID' in process.env) {
    console.log('REACT_APP_OIDC_PROVIDER_ID is set');
} else {
    console.log('REACT_APP_OIDC_PROVIDER_ID not set');
}

if ('REACT_APP_ENVIRONMENT' in process.env) {
    console.log('REACT_APP_ENVIRONMENT is set');
} else {
    console.log('REACT_APP_ENVIRONMENT not set');
}

if ('REACT_APP_IMAGE_VERSION' in process.env) {
    console.log('REACT_APP_IMAGE_VERSION is set');
} else {
    console.log('REACT_APP_IMAGE_VERSION not set');
}
