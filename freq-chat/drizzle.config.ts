import { config } from 'dotenv';
import { defineConfig } from 'drizzle-kit';

config({
  path: '.env.development.local', // Ensure correct .env file is loaded
});

export default defineConfig({
  schema: './lib/db/schema.ts',
  out: './lib/db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    // biome-ignore lint: Forbidden non-null assertion.
    url: process.env.POSTGRES_URL!,
  },
});
