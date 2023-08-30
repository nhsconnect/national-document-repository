#!/bin/sh -eu


if test -f ".env"; then
    rm .env
fi

cp .env.template .env

SEDOPTION='-i ' 
if [ -z "$OSTYPE" -a]; then 
    if ["$OSTYPE" == "darwin"* ]; then
        SEDOPTION='-i '' '
    fi
fi

sed -i '' "s/%DOC_STORE_API_ENDPOINT%/${ENDPOINT_DOC_STORE_API}/" .env
sed -i '' "s/%AWS_REGION%/${AWS_REGION}/" .env
sed -i '' "s/%OIDC_PROVIDER_ID%/${OIDC_PROVIDER_ID}/" .env
sed -i '' "s/%BUILD_ENV%/${BUILD_ENV}/" .env
sed -i '' "s/%IMAGE_VERSION%/${IMAGE_VERSION}/" .env



