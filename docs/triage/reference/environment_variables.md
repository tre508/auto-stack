# 🔧 Environment Variables Reference

**Note:** The strategy for managing environment variables in the `auto-stack` project has been centralized and follows a hierarchical approach.

**The canonical explanation of this new `.env` file hierarchy, including the purpose of the root `.env` file and service-specific `.env` files, can now be found in the Master Setup Guide:**

➡️ **[Understanding the .env File Hierarchy (New Strategy)](../00_MasterSetup.md#31-understanding-the-env-file-hierarchy-new-strategy)**

Please refer to that section in `00_MasterSetup.md` for the most up-to-date information on:
*   Which variables are considered shared and belong in the root `auto-stack/.env`.
*   Which variables are service-specific and belong in files like `controller/.env`, `mem0/.env`, `n8n.env`, etc.
*   The loading order of these files in `docker-compose.yml`.
*   The special considerations for `freq-chat/.env.development.local`.

## Key Principles of the New Strategy:

*   **Centralize Shared Variables:** All variables used by two or more services are in `auto-stack/.env`.
*   **Isolate Service-Specific Variables:** Variables unique to a single service are in its dedicated `.env` file.
*   **Eliminate Duplication:** A variable defined in the root `.env` should not be repeated in service-specific files.

The `.env` files themselves (`auto-stack/.env`, `controller/.env`, etc.) are the ultimate source of truth for specific variable names and their current values. The `00_MasterSetup.md` provides the guiding principles for their organization.

This document previously contained a detailed list of all variables. To avoid redundancy and potential outdated information, that detailed list has been removed in favor of the centralized explanation and the `.env` files themselves.

---
*Last updated: 2025-06-12 (Reflects new centralized .env strategy)*
