from tasks import tasks_service


def tasks_controller(body):
    return tasks_service.create_tasks_service(body)
