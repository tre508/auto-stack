* [ ] **Create per-service data folders on a secondary drive (e.g., D:)**

  * Open a WSL terminal.
  * Run the following commands to create one folder per data‐heavy service (adjust paths if your secondary drive is not mounted as `/mnt/d`):

    ```bash
    mkdir -p /mnt/d/docker-volumes/pg_logs_data
    mkdir -p /mnt/d/docker-volumes/n8n_data
    mkdir -p /mnt/d/docker-volumes/qdrant_data
    mkdir -p /mnt/d/docker-volumes/mem0_data
    ```
  * Confirm that:

    ```
    /mnt/d/docker-volumes/
      ├─ pg_logs_data/
      ├─ n8n_data/
      ├─ qdrant_data/
      └─ mem0_data/
    ```


* [ ] **Open your project workspace and locate your Docker Compose file**

  * In your WSL terminal, navigate to your project root (e.g., `cd ~/projects/auto-stack`).
  * Use your IDE or a text editor to open the `docker-compose.yml` file.

* [ ] **Edit the Compose file: replace named volumes with WSL path bind-mounts**

  1. For each service that has a named volume, find its `volumes:` section.
  2. **Replace**:

     ```yaml
     volumes:
       - automation-stack_pgdata_logging_mcp:/var/lib/postgresql/data
     ```

     **with**:

     ```yaml
     volumes:
       - "/mnt/d/docker-volumes/pg_logs_data:/var/lib/postgresql/data:rw"
     ```

  3. Likewise, replace n8n's volume:

     ```yaml
     volumes:
       - automation-stack_n8n_data_mcp:/home/node/.n8n
     ```

     **with**:

     ```yaml
     volumes:
       - "/mnt/d/docker-volumes/n8n_data:/home/node/.n8n:rw"
     ```
  4. Replace Qdrant's volume:

     ```yaml
     volumes:
       - automation-stack_qdrant_data_mcp:/qdrant/storage
     ```

     **with**:

     ```yaml
     volumes:
       - "/mnt/d/docker-volumes/qdrant_data:/qdrant/storage:rw"
     ```
  5. Replace Mem0's data volume:

     ```yaml
     volumes:
       - automation-stack_mem0_data_mcp:/data
     ```

     **with**:

     ```yaml
     volumes:
       - "/mnt/d/docker-volumes/mem0_data:/data:rw"
     ```
  6. Ensure that any read-only mounts (like `./mem0/server/config.yaml:/app/config.yaml:ro`) stay intact.
  7. **Remove or comment out** the bottom section that declares named volumes, for example:

     ```yaml
     volumes:
       automation-stack_pgdata_logging_mcp:
       automation-stack_n8n_data_mcp:
       automation-stack_qdrant_data_mcp:
       automation-stack_mem0_data_mcp:
     ```

     Because bind-mounts do not rely on Docker-managed volumes.
  8. **Save** the edited `docker-compose.yml`.

* [ ] **Verify permissions on the mounted folders**

  * Docker Desktop for Windows generally handles permissions for bind-mounting Windows directories into WSL 2 containers transparently. The `icacls` command is not needed. If you encounter permissions errors inside a container, ensure the user account running Docker Desktop has access to the folders on the host.

* [ ] **Start your Docker Compose stack**

  * In your WSL terminal (at the project root where `docker-compose.yml` lives):
  * Run:

    ```bash
    docker compose up -d
    ```
  * Wait for all containers to spin up.

* [ ] **Confirm container states and logs**

  * In your WSL terminal, run:

    ```bash
    docker compose ps
    ```

    * Verify that **all required containers** are listed and their STATUS = "Up...".
  * For each data-heavy service, check logs to ensure no errors related to file access:

    ```bash
    docker compose logs postgres_logging_mcp
    docker compose logs n8n_mcp
    docker compose logs qdrant_mcp
    docker compose logs mem0_mcp
    ```

    * Look for lines like "database system is ready to accept connections" (Postgres), "SQLite database opened" (n8n), "Qdrant state loaded" (Qdrant), etc.

* [ ] **Test data writing to each service**

  1. **Postgres**

     * From your WSL terminal or a local client, connect to `localhost:5433` using credentials (`autostack_logger` / `yoursecurepassword_logger`).
     * You can use `docker exec` to run `psql` inside the container:
       ```bash
       docker compose exec postgres_logging_mcp psql -U autostack_logger -d autostack_logs
       ```
     * Inside `psql`, run:

       ```sql
       CREATE TABLE test_check (id SERIAL PRIMARY KEY, note TEXT);
       INSERT INTO test_check (note) VALUES ('Disk test on D:');
       SELECT * FROM test_check;
       \q
       ```
     * On the host, inspect `/mnt/d/docker-volumes/pg_logs_data`—the file `PG_VERSION` and subfolders (`base`, `global`, `pg_wal`, etc.) should have recent timestamps.

  2. **n8n**

     * In your browser, navigate to `http://localhost:5678`.
     * Create a simple workflow or just click around so that `database.sqlite` is created/updated.
     * Check that `/mnt/d/docker-volumes/n8n_data/database.sqlite` exists and its timestamp updated.
     * (Optional) Run from WSL terminal:

       ```bash
       ls -la /mnt/d/docker-volumes/n8n_data
       ```

       * Confirm that `database.sqlite` and any credentials files are present.

  3. **Qdrant**

     * Using `curl` from a WSL terminal, send a health check to `http://localhost:6333/collections`.

       ```bash
       curl http://localhost:6333/collections
       ```
     * If you have the Qdrant Python client installed locally in a venv, you can test insertion.
     * Check that `/mnt/d/docker-volumes/qdrant_data` now contains files under `storage`.

  4. **Mem0**

     * In your browser or via `curl` from WSL, hit the Mem0 API on `http://localhost:7860` (or your mapped port).

       ```bash
       curl http://localhost:7860/health
       ```
     * Create or index a dummy record if Mem0 exposes a REST endpoint.
     * Confirm that files appear under `/mnt/d/docker-volumes/mem0_data`.

* [ ] **Confirm host ↔ container networking**

  * From a script in your WSL project directory (e.g., in a Python venv), attempt to connect to each service. For example, in `~/projects/auto-stack/test_connections.py`:

    ```python
    import psycopg2
    import requests

    # Postgres test
    conn = psycopg2.connect(dbname="autostack_logs", user="autostack_logger", password="yoursecurepassword_logger", host="localhost", port=5433)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM test_check;")
    print("Postgres row count:", cur.fetchone()[0])
    conn.close()

    # n8n test (health or simple workflow query)
    resp = requests.get("http://localhost:5678/health")
    print("n8n status code:", resp.status_code)

    # Qdrant test (collections)
    resp_q = requests.get("http://localhost:6333/collections")
    print("Qdrant collections:", resp_q.json())

    # Mem0 test (health)
    resp_m = requests.get("http://localhost:7860/health")
    print("Mem0 health status:", resp_m.status_code)
    ```
  * Run from your WSL terminal:

    ```bash
    python3 test_connections.py
    ```
  * Verify all services respond successfully.

* [ ] **Clean up old, unused Docker volumes (if any remain)**

  * From your WSL terminal, list all Docker volumes:

    ```bash
    docker volume ls
    ```
  * Remove any leftover named volumes that you replaced with bind mounts (e.g., `automation-stack_pgdata_logging_mcp`, `automation-stack_n8n_data_mcp`, etc.):

    ```bash
    docker volume rm automation-stack_pgdata_logging_mcp automation-stack_n8n_data_mcp automation-stack_qdrant_data_mcp automation-stack_mem0_data_mcp
    ```
  * Confirm they're gone:

    ```bash
    docker volume ls
    ```
  * **Warning:** Only remove volumes you know you no longer need. Deleting a volume is irreversible.

* [ ] **Document your new workflow in the project README**

  * Open `~/projects/auto-stack/README.md`.
  * Add a "Local Development Setup" section with a summary:

    1. Clone repo into WSL (`~/projects/`).
    2. Install Docker Desktop with WSL 2 backend.
    3. Change disk image location to a secondary drive (e.g., `D:\docker-data`).
    4. Create data directories on that drive (e.g., `/mnt/d/docker-volumes/<service>`).
    5. Edit `docker-compose.yml` to use bind-mounts to those directories.
    6. Run `docker compose up -d`.
    7. Test endpoints on `localhost`.
  * Save and commit `README.md`.

* [ ] **Verify overall system health and free up C: drive**

  * In Windows Explorer, check that `C:\ProgramData\DockerDesktop` is now minimal (if you moved Docker's data-root properly).
  * Confirm that most of the large files (images, volumes) now reside on your secondary drive.

* [ ] **Optional: Set up a periodic backup or sync for your data drive**

  * If you need daily backups of these folders, consider scheduling a simple `rsync` script in WSL or using your existing backup solution to include the folders on your secondary drive.
  * For example, to snapshot Postgres data nightly:

    ```bash
    rsync -a --delete /mnt/d/docker-volumes/pg_logs_data/ /mnt/e/backups/pg_logs_data_$(date +%Y%m%d)/
    ```
  * Document this in your project's "Backup" section.

* [ ] **Final confirmation**

  * Confirm all checkboxes above are ticked.
  * Confirm that:

    * Docker's internal disk image is on a secondary drive.
    * Each service's persistent data folder is bind-mounted from `/mnt/d/docker-volumes/<service>`.
    * Host-side programs and your browser can still connect to all containers on `localhost:<port>`.
  * **Mark this guide as complete.**

---

> 🎉 **Congratulations!** You've now rebuilt your entire stack from scratch, moved all heavy data onto a secondary drive, and ensured your C: drive stays lean. All your containers and host programs will talk to each other over `localhost` as before—no extra networking tweaks required.
