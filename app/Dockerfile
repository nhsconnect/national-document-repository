# Build the App
FROM node:24-alpine AS builder
RUN apk add unzip wget
WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
COPY ./ ./

RUN npm install --legacy-peer-deps
RUN mkdir -p ./public/pdfjs
RUN wget https://github.com/mozilla/pdf.js/releases/download/v4.10.38/pdfjs-4.10.38-dist.zip -O ./public/pdfjs/pdfjs.zip
RUN unzip -o -d ./public/pdfjs ./public/pdfjs/pdfjs.zip
RUN rm ./public/pdfjs/pdfjs.zip
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
