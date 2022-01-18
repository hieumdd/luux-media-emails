from libs.emails import send_email
from controllers.reports import report_factory, build_report
from controllers.tasks import create_tasks

SENDER = "siddhantmehandru.developer@gmail.com"
RECEIVERS = [
    "hieumdd@gmail.com",
    # "jhamb285@gmail.com",
    # "kevin@luux-media.com",
]
DATASET = "GoogleAds"
TABLE_SUFFIX = "3413321199"


def main(request) -> dict:
    data: dict = request.get_json()
    print(data)

    if "external_customer_id" in data and "mode" in data:
        subject, report = build_report(
            DATASET,
            TABLE_SUFFIX,
            data["external_customer_id"],
            data["account_name"],
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
        response = create_tasks(DATASET, TABLE_SUFFIX, data)
    else:
        raise ValueError(data)

    print(response)
    return response
