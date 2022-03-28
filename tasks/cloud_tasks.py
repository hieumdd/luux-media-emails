from typing import Any, Callable
import os
import json
import uuid

from google.cloud import tasks_v2
from google import auth

TASKS_CLIENT = tasks_v2.CloudTasksClient()
_, PROJECT_ID = auth.default()
CLOUD_TASKS_PATH = (PROJECT_ID, "us-central1", "luux-media-emails")


def create_tasks(name_fn: Callable[[dict[str, Any]], str]):
    def _create(payloads: list[dict[str, Any]]) -> int:
        tasks = [
            {
                "parent": TASKS_CLIENT.queue_path(*CLOUD_TASKS_PATH),
                "task": {
                    "name": TASKS_CLIENT.task_path(
                        *CLOUD_TASKS_PATH,
                        task=f"{name_fn(payload)}-{uuid.uuid4()}",
                    ),
                    "http_request": {
                        "http_method": tasks_v2.HttpMethod.POST,
                        "url": os.getenv("PUBLIC_URL"),
                        "oidc_token": {
                            "service_account_email": os.getenv("GCP_SA"),
                        },
                        "headers": {"Content-type": "application/json"},
                        "body": json.dumps(payload).encode(),
                    },
                },
            }
            for payload in payloads
        ]
        tasks
        return len([TASKS_CLIENT.create_task(task) for task in tasks])

    return _create
