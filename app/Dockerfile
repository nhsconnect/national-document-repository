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
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY --from=builder /app/build .
WORKDIR /etc/nginx
COPY --from=builder ./app/docker/nginx.conf ./nginx.conf.template
RUN sed "s/\$CONTAINER_PORT/${CONTAINER_PORT}/g" ./nginx.conf.template > ./nginx.conf
EXPOSE ${CONTAINER_PORT}
ENTRYPOINT ["nginx", "-g", "daemon off;"]