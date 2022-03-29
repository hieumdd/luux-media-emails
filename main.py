from report.report_controller import report_controller
from tasks.tasks_service import create_tasks_service


def main(request):
    data = request.get_json()
    print(data)

    if "tasks" in data:
        response = create_tasks_service(data)
    elif "external_customer_id" in data and "report" in data:
        response = report_controller(data)
    else:
        raise ValueError(data)

    print(response)
    return response
