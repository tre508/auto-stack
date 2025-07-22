# Vercel AI Chat: Troubleshooting Guide

**Last updated:** 2025-05-26

This guide helps diagnose and resolve common issues encountered with the Vercel AI Chat service (`freq-chat` for local development, or a Vercel deployment) within the `automation-stack`. Also refer to `setup.md` and `integration.md` for configuration details.

---

## 1. Common Issues & Solutions

### Issue: Connection Refused / 404 Not Found / 502 Bad Gateway (Local `freq-chat` Dev Server)

*   **Symptom:** Unable to access the `freq-chat` UI (e.g., `http://localhost:3000`).
*   **Possible Causes & Troubleshooting Steps:**
    1.  **Dev Server Not Running:**
        *   Ensure the `pnpm run dev` process for `freq-chat` is active in your terminal.
        *   If it crashed, check the terminal output for errors (e.g., "Module not found", database errors, NextAuth errors).
    2.  **Port Conflict:** If port 3000 is in use, Next.js might start on an alternative port (e.g., 3001, 3002). Check the terminal output from `pnpm run dev` for the actual URL (e.g., `✓ Ready on http://localhost:3001`).
    3.  **Firewall Issues:** Ensure your firewall isn't blocking connections to the port Next.js is using.

### Issue: `'next' is not recognized as an internal or external command`

*   **Symptom:** `pnpm run dev` (which executes `next dev --turbo`) fails with this error.
*   **Cause:** `pnpm` cannot find the `next` executable, often due to issues with how `node_modules/.bin` shims are created/linked, especially on Windows.
*   **Solution:**
    1.  Ensure `next` is listed as a dependency in `freq-chat/package.json`.
    2.  Delete `freq-chat/node_modules` and `freq-chat/pnpm-lock.yaml`.
    3.  Run `cd freq-chat; pnpm install --shamefully-hoist`. The `--shamefully-hoist` flag creates a flatter `node_modules` structure that can resolve this on some systems.

### Issue: "Module not found: Can't resolve 'some-package'" (During `pnpm run dev`)

*   **Symptom:** The Next.js build process fails, reporting it cannot find a specific npm package.
*   **Cause:** The required package is imported in the code but not listed in `freq-chat/package.json` or not installed correctly. This was common after merging `package.json` with the Vercel AI Chatbot template.
*   **Solution:**
    1.  Install the missing package: `cd freq-chat; pnpm add some-package`.
    2.  If it's a type-only import, you might need `@types/some-package`: `cd freq-chat; pnpm add -D @types/some-package`.
    3.  Stop and restart the `pnpm run dev` server.

### Issue: TypeScript Errors in VS Code ("Cannot find module", "Cannot find name 'process'")

*   **Symptom:** VS Code's "Problems" tab shows errors even if packages are installed and `pnpm run dev` might compile successfully.
*   **Cause:** VS Code's TypeScript language server cache might be stale or not recognizing type definitions correctly after `node_modules` changes.
*   **Solution:**
    1.  **Restart TS Server:** Open any `.ts` or `.tsx` file in VS Code. Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P), type "TypeScript: Restart TS server", and select it.
    2.  **Check `tsconfig.json`:** Ensure `compilerOptions.typeRoots` or `compilerOptions.types` are correctly set if needed (though usually Next.js handles this). Ensure `@types/node` is in `devDependencies` for `process` and other Node.js globals.
    3.  **Reinstall Specific Types:** If errors persist for specific modules (e.g., `dotenv`), try `pnpm add -D @types/dotenv`.

### Issue: Database Connection or Migration Errors (Local PostgreSQL for `freq-chat`)

*   **Symptom:**
    *   `Error: POSTGRES_URL is not defined` (during `pnpm db:migrate`).
    *   `PostgresError: column "some_column" of relation "SomeTable" already exists` (during `pnpm db:migrate`).
    *   Application runtime errors related to database queries (e.g., "Failed to create guest user").
*   **Possible Causes & Troubleshooting Steps:**
    1.  **`POSTGRES_URL` Not Defined for Scripts:**
        *   Ensure `lib/db/migrate.ts` and `drizzle.config.ts` load environment variables from the correct file (e.g., `.env.development.local`) using `dotenv`.
        *   Verify `POSTGRES_URL` is correctly formatted in `.env.development.local`.
    2.  **"Column already exists" during `migrate`:**
        *   This usually means old migration files in `lib/db/migrations` are conflicting with the current schema or database state.
        *   **Solution:**
            1.  Delete the contents of `freq-chat/lib/db/migrations` (SQL files and `meta` folder).
            2.  Run `cd freq-chat; pnpm db:generate`. It should report "No schema changes, nothing to migrate" if the database matches `lib/db/schema.ts`.
            3.  Run `cd freq-chat; pnpm db:migrate`. It should now complete successfully or report no migrations to apply.
    3.  **General Connection Issues / "Failed to create guest user":**
        *   Verify PostgreSQL server is running.
        *   Confirm `POSTGRES_URL` in `.env.development.local` is correct (user, password, host, port, db name).
        *   Use the `freq-chat/test-db.mjs` script (`node test-db.mjs`) to verify direct DB connectivity and list tables. This helps confirm if tables were created by migrations.
        *   Ensure the database user (`freqchat_user`) has correct privileges on `freqchat_db`.

### Issue: "Wonky UI" / Styling Problems

*   **Symptom:** The `freq-chat` UI renders but styles are incorrect or layout is broken.
*   **Cause:** Likely due to the `package.json` merge which downgraded Tailwind CSS from v4.x (if previously used) to v3.4.1 (from the template).
*   **Solution:**
    1.  **Review `tailwind.config.ts` (or `.js`):** Ensure its syntax and theme configuration are compatible with Tailwind CSS v3. Remove or adapt any v4-specific configurations.
    2.  **Check Global CSS (`app/globals.css`):** Ensure CSS variables (like `--border`) used by Tailwind's theme are correctly defined.
    3.  **Inspect Component Classes:** Look for any Tailwind utility classes that might have changed or been removed between v4 and v3.
    4.  **Address `border-border` Class:** If this class was causing errors, ensure `border` is a defined color in your `tailwind.config.ts` theme's `colors` object, and that you're applying a border-width utility (e.g., `border`) alongside `border-border`.

### Issue: NextAuth.js `headers()` / `cookies()` Warnings

*   **Symptom:** Console warnings like `Route "/api/auth/guest" used ...headers()` or `...cookies().set(...)`. `...should be awaited before using its value.`
*   **Cause:** Related to how NextAuth.js v5 interacts with dynamic APIs in Next.js App Router Route Handlers. Often, these are warnings that don't break functionality if the underlying auth logic is sound.
*   **Solution:**
    1.  Ensure auth functionality (login, guest user creation) is working.
    2.  These warnings are often lower priority. They might be addressed by future updates to Next.js or NextAuth.js, or by refactoring how these dynamic functions are used in the specific route handlers if they cause actual bugs.

---

## 2. Essential Logs for Debugging (Local `freq-chat` Development)

*   **`freq-chat` Dev Server Terminal:** The primary source for build errors ("Module not found"), runtime errors from Next.js or NextAuth.js, and API route issues.
*   **Browser Developer Console:** For client-side JavaScript errors, network request failures from the UI, and React rendering issues.
*   **PostgreSQL Logs:** If database connection or query errors are suspected at a deeper level.
*   **VS Code "Problems" Tab:** For TypeScript type-checking errors.

---

For Vercel cloud deployment troubleshooting, refer to Vercel's documentation and dashboard logs.
For specific customization details of the Next.js AI Chatbot template, refer to `nextjs_ai_chatbot_customization.md`.
