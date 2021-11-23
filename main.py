from google.cloud import bigquery, tasks_v2  # type: ignore

from controllers.reports import report_factory, build_report
from controllers.emails import send_email
from controllers.tasks import create_tasks

SENDER = "siddhantmehandru.developer@gmail.com"
RECEIVERS = [
    "hieumdd@gmail.com",
    "jhamb285@gmail.com",
    "kevin@luux-media.com",
]

BQ_CLIENT = bigquery.Client()
TASKS_CLIENT = tasks_v2.CloudTasksClient()
DATASET = "GoogleAds"
TABLE_SUFFIX = "3413321199"


def main(request) -> dict:
    data = request.get_json()
    print(data)

    if "external_customer_id" in data and "mode" in data:
        subject, report = build_report(
            BQ_CLIENT,
            DATASET,
            TABLE_SUFFIX,
            data["external_customer_id"],
            report_factory(data["mode"]),
        )
        emails_sent = (
            len(
                send_email(
                    SENDER,
                    RECEIVERS,
                    subject,
                    report,
                )
            )
            if report
            else 0
        )
        response = {
            "emails_sent": emails_sent,
        }
    elif "tasks" in data:
        response = create_tasks(BQ_CLIENT, TASKS_CLIENT, DATASET, TABLE_SUFFIX, data)
    else:
        raise ValueError(data)

    print(response)
    return response
