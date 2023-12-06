import AWS from 'aws-sdk';

// set as env vars
AWS.config.update({
    accessKeyId: '',
    secretAccessKey: '',
    region: '',
    sessionToken: '',
});

export default AWS;
