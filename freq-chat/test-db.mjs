import postgres from 'postgres';
import { config } from 'dotenv';

config({ path: '.env.development.local' });

async function testDB() {
  const dbUrl = process.env.POSTGRES_URL;
  if (!dbUrl) {
    console.error('POSTGRES_URL is not set in .env.development.local');
    process.exit(1);
  }

  console.log(`Attempting to connect to: ${dbUrl}`);
  let sql;
  try {
    sql = postgres(dbUrl, {
      onnotice: () => {}, // Suppress notices if any
      max: 1, // Only need one connection for this test
      idle_timeout: 5, // seconds
      connect_timeout: 10, // seconds
    });

    console.log('Successfully created postgres client instance.');

    // Test connection with a simple query
    const result = await sql`SELECT version();`;
    console.log('PostgreSQL version:', result[0].version);

    // List tables in the public schema
    const tables = await sql`
      SELECT tablename
      FROM pg_tables
      WHERE schemaname = 'public'
      ORDER BY tablename;
    `;

    if (tables.length > 0) {
      console.log('\\nTables in public schema:');
      tables.forEach(table => console.log(`- ${table.tablename}`));
    } else {
      console.log('\\nNo tables found in public schema.');
    }

    await sql.end({ timeout: 5 });
    console.log('\\nDatabase connection test successful and client closed.');
  } catch (error) {
    console.error('\\nError during database test:');
    console.error('Error Name:', error.name);
    console.error('Error Message:', error.message);
    if (error.code) {
      console.error('Error Code:', error.code);
    }
    if (error.stack) {
      console.error('Stack Trace:', error.stack);
    }
    if (sql) {
      await sql.end({ timeout: 5 }).catch(err => console.error('Error closing connection:', err));
    }
    process.exit(1);
  }
}

testDB();
