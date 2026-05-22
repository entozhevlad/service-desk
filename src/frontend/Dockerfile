# build
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY index.html ./
COPY env.d.ts ./
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tsconfig.app.json ./
COPY tsconfig.node.json ./
COPY tsconfig.vitest.json ./
COPY src ./src
COPY public ./public

ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# run
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

RUN mkdir -p /var/cache/nginx/client_temp /var/run /var/log/nginx /run \
 && chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx /run /usr/share/nginx/html

USER nginx

EXPOSE 8080
