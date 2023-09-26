# Build the App
FROM node:alpine as builder
WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
COPY ./ ./

RUN npm install --legacy-peer-deps
RUN npm run build

# Host the App
FROM nginx:1.19.0

WORKDIR /usr/share/nginx
RUN rm -rf ./html/*
COPY --from=builder /app/build /html
COPY --from=builder /app/docker/nginx.conf ./
EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]
