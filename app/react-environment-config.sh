#!/bin/sh -eu


if test -f ".env"; then
    rm .env
fi

cp .env.template .env

SEDOPTION='-i ' 

# Enable if you want to use on a mac based machine (OSTYPE does not exist on github actions)
# # if [ -z "$OSTYPE" -a "$OSTYPE" == "darwin"* ]; then
#   SEDOPTION='-i "" '
# # fi

sed $SEDOPTION "s/%DOC_STORE_API_ENDPOINT%/${ENDPOINT_DOC_STORE_API}/" .env
sed $SEDOPTION "s/%AWS_REGION%/${AWS_REGION}/" .env
sed $SEDOPTION "s/%OIDC_PROVIDER_ID%/${OIDC_PROVIDER_ID}/" .env
sed $SEDOPTION "s/%BUILD_ENV%/${BUILD_ENV}/" .env
sed $SEDOPTION "s/%IMAGE_VERSION%/${IMAGE_VERSION}/" .env



