from google.cloud import bigquery

from models import reports
from components.emails import send_email

RECEIVERS = [
    "hieumdd@gmail.com",
]

BQ_CLIENT = bigquery.Client()


def main(request) -> dict:
    request_json = request.get_json()

    if "external_customer_id" in request_json and "mode" in request_json:
        subject, report = reports.reports(
            BQ_CLIENT,
            request_json["external_customer_id"],
            request_json["mode"],
        )()
        response = {
            "emails_sent": len(send_email(RECEIVERS, subject, report)),
        }
    return response
