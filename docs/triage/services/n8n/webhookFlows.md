## Status: ✅ New

# n8n Webhook Integration with FastAPI Controller

This document outlines how n8n workflows can interact with the `automation-stack/controller/controller.py` service using webhooks, particularly focusing on the `/execute` and `/notify` endpoints.

The controller acts as a central API gateway for certain operations within the `automation-stack`, and n8n can leverage it to trigger or be triggered by various processes.

---

## Step-by-Step Guide: FastAPI Controller & n8n Webhook Integration

### 1. Running the FastAPI Controller Locally

**A. Using Docker Compose (Recommended):**
- Ensure your `docker-compose.yml` includes the controller service, e.g.:
  ```yaml
  controller_mcp:
    build: ./controller
    ports:
      - "5050:5050"
    environment:
      N8N_WEBHOOK_URL: "http://n8n_mcp:5678/webhook/your-master-workflow-id"
    depends_on:
      - n8n_mcp
  ```
- Start the service:
  ```sh
  docker-compose up -d controller_mcp
  ```
- Confirm it's running:
  ```sh
  curl http://localhost:5050/status
  ```

**B. Manual (Local Python):**
- Install dependencies:
  ```sh
  pip install fastapi uvicorn requests
  ```
- Set the `N8N_WEBHOOK_URL` environment variable:
  ```sh
  export N8N_WEBHOOK_URL="http://localhost:5678/webhook/your-master-workflow-id"
  ```
- Run the controller:
  ```sh
  uvicorn controller.controller:app --reload --port 5050
  ```

---

### 2. Making Test Requests to `/execute` and `/notify`

**A. Using `curl`:**

- **/execute:**
  ```sh
  curl -X POST http://localhost:5050/api/v1/execute \
    -H "Content-Type: application/json" \
    -d '{"task_name": "example_task", "data": {"param1": "value1", "param2": 123}, "source": "external_service_A"}'
  ```

- **/notify:**
  ```sh
  curl -X POST http://localhost:5050/api/v1/notify \
    -H "Content-Type: application/json" \
    -d '{"event_type": "workflow_completed", "workflow_id": "xyz123", "status": "success", "details": "Processed 100 items."}'
  ```

**B. Using Postman:**
- Set method to POST, URL to the endpoint, and body to raw JSON as above.

---

### 3. Example Python Client Code

```python
import requests

# /execute endpoint
execute_payload = {
    "task_name": "example_task",
    "data": {"param1": "value1", "param2": 123},
    "source": "external_service_A"
}
resp = requests.post("http://localhost:5050/api/v1/execute", json=execute_payload)
print("/execute response:", resp.json())

# /notify endpoint
notify_payload = {
    "event_type": "workflow_completed",
    "workflow_id": "xyz123",
    "status": "success",
    "details": "Processed 100 items."
}
resp = requests.post("http://localhost:5050/api/v1/notify", json=notify_payload)
print("/notify response:", resp.json())
```

---

### 4. n8n Workflow Setup

**A. Receiving Webhooks from Controller (/execute):**
1. Create a new workflow in n8n.
2. Add a "Webhook" node (POST) and copy its URL.
3. Set this URL as the `N8N_WEBHOOK_URL` in your controller's environment.
4. Add downstream nodes to process the payload (e.g., Set, Function, HTTP Request, Respond to Webhook).

**B. Sending Notifications to Controller (/notify):**
1. At the end of your n8n workflow, add an "HTTP Request" node.
2. Set method to POST, URL to `http://controller_mcp:5050/api/v1/notify` (or your host/port).
3. Set body to JSON and map fields as needed (e.g., event_type, workflow_id, status, details).

---

### 5. Troubleshooting Tips
- **Controller not forwarding to n8n?**
  - Check that `N8N_WEBHOOK_URL` is set and reachable from the controller container.
  - Inspect controller logs for errors.
- **n8n not receiving requests?**
  - Confirm the webhook node is active (workflow must be active in n8n).
  - Check n8n logs for incoming requests.
- **CORS or network issues?**
  - Ensure all services are on the same Docker network or can reach each other by hostname.
- **Payload format errors?**
  - Validate your JSON payloads with a linter or Postman.
- **Testing locally?**
  - Use `localhost` and mapped ports, or Docker service names if inside containers.

---

## 1. Controller's `/execute` Endpoint: Triggering n8n Workflows

The primary mechanism for n8n to be triggered *by the controller* or *via the controller* is through the controller's `/execute` endpoint.

*   **Endpoint:** `POST /execute`
*   **Purpose:** This endpoint on the controller is designed to receive a task or payload and forward it to a predefined n8n master webhook. This allows other services or manual actions to indirectly trigger specific n8n workflows by calling the controller.
*   **Payload:** The endpoint expects a JSON object (`dict` in Python) as the payload. This payload will be directly passed on to the n8n webhook.
    ```json
    {
      "task_name": "example_task",
      "data": {
        "param1": "value1",
        "param2": 123
      },
      "source": "external_service_A"
    }
    ```
*   **Controller Logic:**
    1.  Receives the POST request with the JSON payload.
    2.  Reads the `N8N_WEBHOOK_URL` environment variable. This variable **must** be configured for the controller to specify the target n8n webhook URL.
    3.  Forwards the received payload as a JSON POST request to the `N8N_WEBHOOK_URL`.
    4.  Returns a confirmation message along with the response from the n8n webhook.
*   **n8n Workflow Setup:**
    *   In n8n, you would have a workflow that starts with a "Webhook" node.
    *   The URL of this n8n Webhook node is what you would set as the `N8N_WEBHOOK_URL` environment variable for the controller service.
    *   This n8n workflow would then process the payload received from the controller.

### Example Flow:

1.  An external application or a user makes a POST request to `http://controller.localhost/api/v1/execute` (assuming Traefik routing) with a specific JSON payload.
2.  The `controller_mcp` service receives this request.
3.  The controller forwards the payload to the `N8N_WEBHOOK_URL` (e.g., `http://n8n_mcp:5678/webhook/your-master-workflow-id`).
4.  The target n8n workflow is triggered and processes the payload.

This pattern is useful for centralizing how n8n workflows are triggered and for adding an intermediary layer (the controller) if needed for authentication, validation, or logging before a task is passed to n8n.

## 2. Controller's `/notify` Endpoint: Sending Information to the Controller

The controller also has a `/notify` endpoint that can be used by n8n (or other services) to send information to the controller.

*   **Endpoint:** `POST /notify`
*   **Purpose:** This endpoint allows external services or workflows to send a notification or a simple data payload to the controller. The controller currently logs this information.
*   **Payload:** Expects a JSON object (`dict`).
    ```json
    {
      "event_type": "workflow_completed",
      "workflow_id": "xyz123",
      "status": "success",
      "details": "Processed 100 items."
    }
    ```
*   **Controller Logic:**
    1.  Receives the POST request with the JSON payload.
    2.  Logs the received payload.
    3.  Returns a confirmation message.
*   **n8n Workflow Setup:**
    *   An n8n workflow can use an "HTTP Request" node to send a POST request to the controller's `/notify` endpoint (e.g., `http://controller_mcp:8000/api/v1/notify`).

### Example Use Case:

1.  An n8n workflow finishes a complex task (e.g., daily data processing).
2.  The last step in the n8n workflow is an HTTP Request node that calls the controller's `/notify` endpoint with a payload indicating the workflow's completion status and any relevant summary.
3.  The controller logs this notification. (In the future, this could trigger other actions within the controller's domain).

## 3. General n8n Webhook Patterns

Beyond these specific controller endpoints, n8n itself is fundamentally designed around webhooks:

*   **Triggering n8n Workflows:** Most n8n workflows start with a Webhook node, which provides a unique URL. Any service that can make an HTTP request can trigger this workflow by sending a request (GET or POST with a body) to that URL.
*   **n8n Calling Other Webhooks:** n8n workflows can use the "HTTP Request" node to call webhooks exposed by any other service, including other n8n workflows, Freqtrade's API (if webhooks were enabled there), or any third-party service.

When designing integrations:

*   Consider if the controller needs to be an intermediary (as with `/execute`). This can be useful for standardizing an API entry point or adding a layer of control.
*   For direct n8n workflow triggers where no intermediary logic is needed from the controller, services can call the n8n Webhook node URL directly.
*   For n8n to call other services, use the HTTP Request node.

By understanding these patterns and the specific endpoints available on the `controller.py` service, you can effectively design and implement robust webhook-based communication flows within the `automation-stack`.

---

## 6. Integrating WhatsApp, Email, and Other External Channels as Workflow Triggers

n8n can receive commands from users via WhatsApp, email, or other supported channels, and route them to your agent workflows (e.g., CentralBrain_Agent):

- **WhatsApp:** Use WhatsApp Cloud API node, Twilio WhatsApp, or a webhook from a WhatsApp bot. Incoming messages trigger the agent workflow. The response is sent back to the user via WhatsApp.
- **Email:** Use IMAP Email Trigger node to watch a dedicated inbox. On new email, extract the command and trigger the agent workflow. Send the result back via Email Send node.
- **Other Channels:** n8n supports Telegram, Slack, Discord, etc.—same pattern applies.

**Example Flow:**
1. User sends a WhatsApp message or email (e.g., "run backtest on BTCUSDT").
2. n8n receives the message, parses the command, and triggers the CentralBrain_Agent workflow.
3. CentralBrain_Agent processes the command, aggregates the result.
4. n8n sends the response back to the user via the original channel.

**Best Practices:**
- Restrict access to trusted users (whitelist numbers/emails).
- Log all incoming/outgoing messages for audit.
- Handle errors gracefully and notify user if command fails.
- Document endpoints and update your workflow docs as new channels are added.

This pattern makes your agent system accessible from anywhere, not just via web dashboards or internal APIs. 