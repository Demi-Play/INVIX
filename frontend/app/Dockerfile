FROM node:22-alpine AS builder

ENV NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine AS runtime

# адрес backend внутри docker-сети
ENV BACKEND_UPSTREAM=http://backend:5000

RUN addgroup -g 1001 app \
    && adduser -u 1001 -G app -D -H -s /sbin/nologin app \
    && sed -i 's|^user  nginx;|# user disabled|' /etc/nginx/nginx.conf \
    && sed -i 's|^pid        /run/nginx.pid;|pid /tmp/nginx.pid;|' /etc/nginx/nginx.conf \
    && rm -f /etc/nginx/conf.d/default.conf \
    && mkdir -p /tmp/nginx \
    && chown -R app:app /var/cache/nginx /etc/nginx/conf.d /var/log/nginx /tmp/nginx

WORKDIR /app

COPY --from=builder --chown=app:app /build/dist ./html
COPY --chown=app:app nginx/default.conf.template /etc/nginx/templates/default.conf.template

USER app
EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=5 \
    CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/"]

CMD ["nginx", "-g", "daemon off;"]
