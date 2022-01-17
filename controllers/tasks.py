import os
import json
import uuid

from google.cloud import tasks_v2
from google import auth

from libs.bigquery import get_customers

TASKS_CLIENT = tasks_v2.CloudTasksClient()
_, PROJECT_ID = auth.default()
CLOUD_TASKS_PATH = (PROJECT_ID, "us-central1", "luux-media-emails")


def create_tasks(dataset: str, table_suffix: str, tasks_data: dict) -> dict:
    accounts = get_customers(dataset, table_suffix)
    payloads = [
        {
            "name": f"{account['ExternalCustomerId']}-{uuid.uuid4()}",
            "payload": {
                "external_customer_id": account["ExternalCustomerId"],
                "account_name": account["AccountDescriptiveName"],
                "mode": tasks_data["tasks"],
            },
        }
        for account in accounts
    ]
    tasks = [
        {
            "name": TASKS_CLIENT.task_path(
                *CLOUD_TASKS_PATH, task=str(payload["name"])
            ),
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": os.getenv("PUBLIC_URL"),
                "oidc_token": {
                    "service_account_email": os.getenv("GCP_SA"),
                },
                "headers": {"Content-type": "application/json"},
                "body": json.dumps(payload["payload"]).encode(),
            },
        }
        for payload in payloads
    ]
    return {
        "messages_sent": len(
            [
                TASKS_CLIENT.create_task(
                    request={
                        "parent": TASKS_CLIENT.queue_path(*CLOUD_TASKS_PATH),
                        "task": task,
                    }
                )
                for task in tasks
            ]
        ),
        "tasks_data": tasks_data,
    }
