# Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY --chown=node:node package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy application code
COPY --chown=node:node . .

# Expose port
EXPOSE 3000

USER node

# Run development server
CMD ["npm", "start"]
