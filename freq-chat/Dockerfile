# Use the official Node.js 18 image
FROM node:18-alpine

# Argument to be passed from docker-compose.yml
ARG POSTGRES_URL_BUILD_ARG

# Set the working directory
WORKDIR /app

# Copy package.json and pnpm-lock.yaml
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN npm install -g pnpm
RUN pnpm install

# Copy necessary directories and files
COPY public ./public
COPY app ./app
COPY components ./components
COPY lib ./lib
COPY hooks ./hooks
COPY artifacts ./artifacts
COPY next.config.ts .
COPY postcss.config.mjs .
COPY tailwind.config.ts .
COPY tsconfig.json .

# Make POSTGRES_URL available as an environment variable for the build step
ENV POSTGRES_URL=${POSTGRES_URL_BUILD_ARG}

# Build the application - only Next.js build, no migrations
RUN pnpm exec next build

# Expose the port the app runs on
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]
