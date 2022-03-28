from report.report_controller import report_controller
from tasks.tasks_controller import tasks_controller


def main(request) -> dict:
    data = request.get_json()
    print(data)

    if "tasks" in data:
        response = tasks_controller(data)
    elif "external_customer_id" in data and "report" in data:
        response = report_controller(data)
    else:
        raise ValueError(data)

    print(response)
    return response
