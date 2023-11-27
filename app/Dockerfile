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
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY --from=builder /app/build .
WORKDIR /etc/nginx
COPY --from=builder ./app/docker/nginx.conf .
EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]