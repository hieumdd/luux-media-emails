from report import report_service


def report_controller(data):
    return {
        "email_sent": report_service.report_service(data),
    }
