# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Configure npm to retry on network errors
RUN npm config set fetch-retries 5 \
    && npm config set fetch-retry-mintimeout 20000

# Install dependencies using npm ci for reproducible installs
RUN npm ci --no-audit --progress=false

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
