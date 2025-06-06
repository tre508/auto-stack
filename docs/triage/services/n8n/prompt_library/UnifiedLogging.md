# Unified Logging for Multi-Agent Automation Systems

---

## Overview
A unified logging setup is essential for observability, debugging, and auditability in multi-agent automation stacks (e.g., n8n + Freqtrade/FreqAI). This document compares methods for building a unified logging system, including when to use a single database/table versus isolated databases for complex agents.

---

## Method 1: Single Database, Unified Logs Table

### **How It Works**
- All agents write to a single database (e.g., `automation_stack` or `centralbrain_logs`).
- A single `logs` table contains all log entries, with an `agent` or `workflow` field to distinguish sources.

### **Example Schema**
```sql
CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    agent VARCHAR(64),
    workflow VARCHAR(64),
    action TEXT,
    status VARCHAR(16),
    details JSONB,
    error TEXT
);
```

### **Pros**
- Centralized: Easy to search, aggregate, and correlate logs across agents.
- Simpler management: Fewer databases to maintain, backup, and secure.
- Scalable: PostgreSQL can handle logs from many agents.
- Flexible queries: Filter by agent, workflow, status, etc.
- Lower operational overhead.

### **Cons**
- Potential for table bloat if not managed (partitioning/archiving may be needed).
- All agents must agree on schema (or use a flexible format like JSONB for details).
- Less isolation: A bug in one agent could (in rare cases) affect logging for others.

---

## Method 2: Isolated Databases for Complex Agents

### **How It Works**
- Most agents log to the unified table as above.
- Exception: Highly complex or high-volume agents (e.g., custom ML pipelines, regulatory separation) use their own dedicated database and schema.

### **Pros**
- Strong isolation: Faults or schema changes in one agent do not affect others.
- Custom schemas: Each agent can optimize its log structure.
- Useful for regulatory or multi-tenant requirements.
- Can scale independently if one agent is extremely high-volume.

### **Cons**
- Harder to aggregate/search logs across agents (requires cross-DB queries or ETL).
- More operational overhead (backups, migrations, credentials).
- Risk of data silos.

---

## Best Practices
- **Default:** Use a single DB and logs table with an `agent` field for most agents.
- **Exception:** Use isolated DBs only for agents with special requirements (e.g., compliance, scale, custom analytics).
- **Schema:** Use a flexible schema (e.g., JSONB for details) to accommodate evolving log formats.
- **Retention:** Implement log rotation, partitioning, or archiving for large tables.
- **Security:** Restrict write access to logging tables; use roles/permissions.
- **Monitoring:** Set up alerts for logging failures or anomalies.

---

## Recommendations
- For most automation stacks, a unified logging table in a single PostgreSQL database is optimal.
- Isolated DBs should be reserved for rare, well-justified cases.
- Document all logging endpoints and schemas for maintainability.

---

## Recommended Logging Pattern (Update)

- **n8n as Logging Orchestrator:**
  - All persistent, structured logs should be written to PostgreSQL by n8n workflows, not directly by the controller or other services.
  - The controller should log to stdout and (optionally) a local file for debugging and diagnostics.
  - n8n workflows triggered by the controller (or any agent workflow) should include a "Postgres" node to log actions, status, errors, and details to the unified log table.

### Example: n8n Postgres Node for Logging

- Add a "Postgres" node to your workflow with the following mapping:
  - `agent`: e.g., `CentralBrain_Agent`
  - `workflow`: e.g., `Backtest_Agent`
  - `action`: e.g., `run_backtest`
  - `status`: e.g., `success` or `error`
  - `details`: JSON object with relevant context
  - `error`: error message if any

This keeps the controller simple and all logging logic centralized in n8n, making it easy to maintain, update, and scale.

---

**Next Steps:**
- Implement the unified logging schema in your main database.
- Configure all agents to log to this table, using the `agent` field for separation.
- For any agent requiring isolation, document the rationale and schema. 