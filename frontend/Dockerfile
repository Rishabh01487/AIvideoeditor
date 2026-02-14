# Frontend Dockerfile for AI Video Editor Platform
# Stage 1: Build
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --verbose

# Copy source code
COPY . .

# Build application
ARG REACT_APP_API_URL=/api
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN npm run build

# Stage 2: Serve
FROM nginx:1.25-alpine

# Copy nginx configuration
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts
COPY --from=build /app/build /usr/share/nginx/html

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
