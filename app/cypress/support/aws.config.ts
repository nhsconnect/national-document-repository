import AWS from 'aws-sdk';

// need to get from env vars
AWS.config.update({
    accessKeyId: '',
    secretAccessKey: '',
    region: '',
    sessionToken: '',
});

export default AWS;
