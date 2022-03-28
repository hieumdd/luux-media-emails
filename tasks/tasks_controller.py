from typing import Any, TypedDict

from tasks import tasks_service

services: dict[str, Any] = {
    "account": tasks_service.create_account_tasks,
    "mcc": tasks_service.create_mcc_tasks,
}


class TaskRequest(TypedDict):
    tasks: str


def tasks_controller(body: TaskRequest):
    return services[body["tasks"]](body)
