# Stage 1
ARG BUILD_ENV
FROM node:20.19.0 as node
WORKDIR /app
COPY its_ui/ .
RUN npm install

ARG BUILD_ENV
RUN npm run build -- --configuration ${BUILD_ENV}

# Stage 2
FROM nginx:latest
COPY --from=node /app/dist/its_ui /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf
COPY runtime-config.sh /docker-entrypoint.d/40-runtime-config.sh
RUN chmod +x /docker-entrypoint.d/40-runtime-config.sh