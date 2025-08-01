# E2E Tests

These tests focus on the features of the NDR. This will serve as a blended suite of integration and end-to-end (E2E) tests, with the aim to be more focused on the integration testing of the NDR.

In order to execute these tests you will need to have a default AWS configuration pointed to your environment under tests.

In addition the following AWS Environment Variables need to be set in order to use the E2e Tests

| Environment Variable | Description                                                   |
| -------------------- | ------------------------------------------------------------- |
| `NDR_API_KEY`        | The API key required to authenticate requests to the NDR API. |
| `NDR_API_ENDPOINT`   | The URI string used to connect to the NDR API.                |
| `NDR_S3_BUCKET`      | The name of the Lloyd George Store.                           |
| `NDR_DYNAMO_STORE`   | The name of the Lloyd George Reference Data Store.            |

# Snapshots

Snapshots reduce the amount of individual assertions by comparing pre and post an object e.g. a JSON returned from an API
To update snapshots you can run pytest with the additional argument `--snapshot-update` this will replace the existing snapshots

`make test-api-e2e
make test-api-e2e-snapshots`
