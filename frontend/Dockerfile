# Frontend Dockerfile
FROM node:24-alpine

WORKDIR /app

# Transfer ownership of the app directory to the user node
RUN chown -R node:node /app

# Copy package files with node as the owner
COPY --chown=node:node package.json package-lock.json* ./

# Switch to a non-root user (node) for security
USER node

# Install dependencies
RUN npm ci

# Copy application code with node as the owner
COPY --chown=node:node . .

# Expose port
EXPOSE 3000

# Run development server
CMD ["npm", "start"]
