# Build the App
FROM node:18-alpine as builder
WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
COPY ./ ./

RUN npm install --legacy-peer-deps
RUN npm run build

# Host the App
FROM nginx:latest
ARG CONTAINER_PORT
ARG CLOUDFRONT_DOMAIN_NAME
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY --from=builder /app/dist .

WORKDIR /etc/nginx
COPY --from=builder ./app/docker/nginx.conf ./nginx.conf.template

RUN sed -i "s/\$CONTAINER_PORT/${CONTAINER_PORT}/g" ./nginx.conf.template
RUN sed "s/\$CLOUDFRONT_DOMAIN_NAME/${CLOUDFRONT_DOMAIN_NAME}/g" ./nginx.conf.template > ./nginx.conf

EXPOSE ${CONTAINER_PORT}
ENTRYPOINT ["nginx", "-g", "daemon off;"]
