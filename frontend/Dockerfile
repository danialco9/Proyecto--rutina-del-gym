# syntax=docker/dockerfile:1

# Build: install the locked dependencies and compile the single-page app.
FROM node:24-alpine AS build
RUN npm install --global pnpm@12.4.1
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
# Vite inlines VITE_* variables at build time.
ARG VITE_DEMO_ENABLED=false
ENV VITE_DEMO_ENABLED=$VITE_DEMO_ENABLED
RUN pnpm build

# Runtime: nginx serves the static files and forwards /api to the backend on the same origin.
FROM nginx:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
