# Multi-stage build:
#   stage 1 (node)  - install deps and produce the static production bundle
#   stage 2 (nginx) - serve those static files + proxy /api to the backend
# The final image contains only nginx + built assets (small, no Node runtime).

# --- build stage ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# --- serve stage ---
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
