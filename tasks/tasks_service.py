from compose import compose

from report import report
from db.bigquery import get_customers
from tasks import cloud_tasks

MCC: list[report.MCC] = [
    {
        "dataset": "GoogleAds",
        "table_suffix": "3413321199",
    }
]


def create_account_tasks(body: report.MCCRequest) -> int:
    return compose(
        cloud_tasks.create_tasks(lambda x: f"{x['dataset']-x['report']}"),
        lambda x: [{**y, "report": body["report"]} for y in x],
        get_customers,
    )(
        {
            "dataset": body["dataset"],
            "table_suffix": body["table_suffix"],
        }
    )


def create_mcc_tasks(*args) -> int:
    return cloud_tasks.create_tasks(lambda x: f"{x['report']}")(
        [{**i, "report": body["report"], "tasks": "account"} for i in MCC]  # type: ignore
    )
