# Use an official Node.js runtime as a parent image
FROM node:18-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json (if available) an yarn.lock (if available)
COPY package*.json ./
# COPY yarn.lock ./

# Install app dependencies
# If you have a package-lock.json, using `npm ci` is recommended for reproducible builds
RUN npm install --omit=dev
# Or, if using yarn: 
# RUN yarn install --production

# Bundle app source
COPY . .

# Make port 8000 available to the world outside this container
# This will be the default port, but can be overridden by PROXY_PORT env var in server.js
EXPOSE 8000

# Define environment variables (can be overridden at runtime)
ENV NODE_ENV=production
# PROXY_PORT defaults to 8000 in server.js if not set
# OPENROUTER_KEY must be provided at runtime

# Command to run the application
CMD [ "node", "server.js" ] 