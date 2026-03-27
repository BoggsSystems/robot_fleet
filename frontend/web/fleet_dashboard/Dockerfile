# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (use ci for cleaner installs, fallback to install)
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Clean npm cache and reinstall ajv if needed
RUN npm cache clean --force && npm install ajv@8 --save-dev --legacy-peer-deps 2>/dev/null || true

# Copy source code
COPY . .

# Build the app (URLs can be overridden at build time)
ARG REACT_APP_AUTH_URL=https://robotfleet-auth.kindmoss-6eac8399.eastus.azurecontainerapps.io
ARG REACT_APP_API_URL=https://robotfleet-ai.kindmoss-6eac8399.eastus.azurecontainerapps.io
ENV REACT_APP_AUTH_URL=${REACT_APP_AUTH_URL}
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/build /usr/share/nginx/html

# Create nginx config file
RUN printf 'server {\n    listen 80;\n    server_name localhost;\n    location / {\n        root /usr/share/nginx/html;\n        index index.html;\n        try_files $uri $uri/ /index.html;\n    }\n}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
