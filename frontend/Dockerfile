# Stage 1
ARG BUILD_ENV
FROM node:18.17.1 as node
WORKDIR /app
COPY its_ui/ .
RUN npm install

ARG BUILD_ENV
RUN npm run build -- --configuration ${BUILD_ENV}

# Stage 2
FROM nginx:latest
COPY --from=node /app/dist/its_ui /usr/share/nginx/html