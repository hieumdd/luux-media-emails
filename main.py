from google.cloud import bigquery

from models import reports
from components.emails import send_email
from tasks import tasks

RECEIVERS = [
    "hieumdd@gmail.com",
    "jhamb285@gmail.com",
]

BQ_CLIENT = bigquery.Client()


def main(request) -> dict:
    request_json = request.get_json()
    print(request_json)

    if "external_customer_id" in request_json and "mode" in request_json:
        subject, report = reports.reports(
            BQ_CLIENT,
            request_json["external_customer_id"],
            request_json["mode"],
        )()
        response = {
            "emails_sent": len(send_email(RECEIVERS, subject, report)),
        }
    elif "tasks" in request_json:
        response = tasks(BQ_CLIENT, request_json)
    else:
        raise ValueError(request_json)

    print(response)
    return response
