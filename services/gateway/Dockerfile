# ─── Stage 1: Build Frontend ──────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ .
RUN npm run build

# ─── Stage 2: Nginx Gateway ──────────────────
FROM nginx:1.25-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY services/gateway/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /build/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
