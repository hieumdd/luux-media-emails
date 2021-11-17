import os
import json
import uuid

from google.cloud import tasks_v2, bigquery  # type: ignore
from google import auth

SERVICE_ACCOUNT, PROJECT_ID = auth.default()
CLOUD_TASKS_PATH = (PROJECT_ID, "us-central1", "luux_media_emails")


def get_customers(
    client: bigquery.Client,
    dataset: str,
    table_suffix: str,
) -> list[str]:
    results = client.query(
        f"SELECT DISTINCT ExternalCustomerId FROM {dataset}.AccountStats_{table_suffix}"
    ).result()
    rows = [dict(row.items()) for row in results]
    return [str(i["ExternalCustomerId"]) for i in rows]


def create_tasks(
    task_client: tasks_v2.CloudTasksClient,
    bq_client: bigquery.Client,
    dataset: str,
    table_suffix: str,
    tasks_data: dict,
) -> dict:
    accounts = get_customers(bq_client, dataset, table_suffix)
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
            "name": task_client.task_path(*CLOUD_TASKS_PATH, task=str(payload["name"])),
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": os.getenv("PUBLIC_URL"),
                "oidc_token": {
                    "service_account_email": SERVICE_ACCOUNT.service_account_email,
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
                task_client.create_task(
                    request={
                        "parent": task_client.queue_path(*CLOUD_TASKS_PATH),
                        "task": task,
                    }
                )
                for task in tasks
            ]
        ),
        "tasks_data": tasks_data,
    }
