from google.cloud import bigquery

from controllers.reports import report_factory, build_report
from controllers.emails import send_email
from tasks import tasks

SENDER = "siddhantmehandru.developer@gmail.com"
RECEIVERS = [
    "hieumdd@gmail.com",
    "jhamb285@gmail.com",
]

BQ_CLIENT = bigquery.Client()
DATASET = "GoogleAds"
TABLE_SUFFIX = "7248313550"


def main(request) -> dict:
    request_json = request.get_json()
    print(request_json)

    if "external_customer_id" in request_json and "mode" in request_json:
        subject, report = build_report(
            BQ_CLIENT,
            DATASET,
            TABLE_SUFFIX,
            request_json["external_customer_id"],
            report_factory(request_json["mode"]),
        )
        response = {
            "emails_sent": len(
                send_email(
                    SENDER,
                    RECEIVERS,
                    subject,
                    report,
                )
            ),
        }
    elif "tasks" in request_json:
        response = tasks(BQ_CLIENT, request_json)
    else:
        raise ValueError(request_json)

    print(response)
    return response
