import requests
import json
import sys
import os

# Base URL for n8n
base_url = "http://localhost:5678"

# The API key from .env
api_key = os.environ.get('N8N_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNzRiYzU4MS05ZmEyLTQ0YjctYTkwMS01NTQyZjZiZGViMTQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzQ2Nzk0MjE5fQ.ZtDEw9Aq14LjJhMo8UevrYLW-kKp0GM32CRuCPVbiok')

# Headers for authentication
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-N8N-API-KEY": api_key
}

# Simple test workflow definition
workflow = {
    "name": "Connectivity Test Workflow",
    "nodes": [
        {
            "parameters": {
                "path": "test",
                "responseMode": "responseNode",
                "options": {}
            },
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "position": [
                580,
                300
            ],
            "typeVersion": 1
        },
        {
            "parameters": {
                "options": {}
            },
            "name": "Respond to Webhook",
            "type": "n8n-nodes-base.respondToWebhook",
            "position": [
                920,
                300
            ],
            "typeVersion": 1
        }
    ],
    "connections": {
        "Webhook": {
            "main": [
                [
                    {
                        "node": "Respond to Webhook",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "active": True,
    "settings": {},
    "tags": ["test", "connectivity"]
}

def create_workflow():
    """Create a test workflow in n8n"""
    try:
        response = requests.post(
            f"{base_url}/rest/workflows", 
            headers=headers, 
            json=workflow
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Workflow created successfully!")
            print(f"ID: {result.get('id')}")
            print(f"Name: {result.get('name')}")
            print(f"Webhook URL: {base_url}/webhook/{result.get('id')}/test")
            return True
        else:
            print(f"Failed to create workflow: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error creating workflow: {e}")
        return False

if __name__ == "__main__":
    print("Creating test workflow in n8n...")
    success = create_workflow()
    
    if success:
        print("\nTest the webhook with:")
        print(f'curl -X POST {base_url}/webhook/test -H "Content-Type: application/json" -d "{{\\"message\\": \\"hello\\"}}"')
        sys.exit(0)
    else:
        print("Failed to create test workflow.")
        sys.exit(1) 