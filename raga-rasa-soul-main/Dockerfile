# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application with API base URL pointing to backend
ARG VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built app from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
