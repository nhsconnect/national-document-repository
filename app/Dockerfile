# Build the App
FROM node:alpine as builder
WORKDIR /app
COPY package.json ./
COPY package-lock.json ./
COPY ./ ./
RUN npm i

RUN npm run build

# Host the App
FROM nginx:1.19.0

ENV REACT_CONFIG_API_ENDPOINT=""
ENV REACT_CONFIG_AWS_REGION=""

WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY --from=builder /app/build .

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

COPY --from=builder /app/docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]