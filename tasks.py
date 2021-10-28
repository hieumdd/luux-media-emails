import os
import json
import uuid

from google.cloud import tasks_v2, bigquery

from config import DATASET, TABLE_SUFFIX


TASKS_CLIENT = tasks_v2.CloudTasksClient()
CLOUD_TASKS_PATH = (
    os.getenv("PROJECT_ID"),
    "us-central1",
    "luux_media_emails",
)
PARENT = TASKS_CLIENT.queue_path(*CLOUD_TASKS_PATH)


def get_customers(client: bigquery.Client) -> list[str]:
    results = client.query(
        f"SELECT DISTINCT ExternalCustomerId FROM {DATASET}.AccountStats_{TABLE_SUFFIX}"
    ).result()
    rows = [dict(row.items()) for row in results]
    return [str(i["ExternalCustomerId"]) for i in rows]


def tasks(client: bigquery.Client, tasks_data: dict) -> dict:
    accounts = get_customers(client)
    payloads = [
        {
            "name": f"{account}-{uuid.uuid4()}",
            "payload": {
                "external_customer_id": account,
                "mode": tasks_data["tasks"],
            },
        }
        for account in accounts
    ]
    tasks = [
        {
            "name": TASKS_CLIENT.task_path(*CLOUD_TASKS_PATH, task=payload["name"]),
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": os.getenv("PUBLIC_URL"),
                "oidc_token": {
                    "service_account_email": os.getenv("GCP_SA"),
                },
                "headers": {
                    "Content-type": "application/json",
                },
                "body": json.dumps(payload["payload"]).encode(),
            },
        }
        for payload in payloads
    ]
    responses = [
        TASKS_CLIENT.create_task(
            request={
                "parent": PARENT,
                "task": task,
            }
        )
        for task in tasks
    ]
    return {
        "messages_sent": len(responses),
        "tasks_data": tasks_data,
    }
