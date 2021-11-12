import os
import json
import uuid

from google.cloud import tasks_v2, bigquery  # type: ignore


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


def tasks(
    task_client: tasks_v2.CloudTasksClient,
    bq_client: bigquery.Client,
    dataset: str,
    table_suffix: str,
    tasks_data: dict,
) -> dict:
    cloud_tasks_path = (
        os.getenv("PROJECT_ID", ""),
        "us-central1",
        "luux_media_emails",
    )
    parent = task_client.queue_path(*cloud_tasks_path)
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
            "name": task_client.task_path(*cloud_tasks_path, task=str(payload["name"])),
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
        task_client.create_task(
            request={
                "parent": parent,
                "task": task,
            }
        )
        for task in tasks
    ]
    return {
        "messages_sent": len(responses),
        "tasks_data": tasks_data,
    }
