from report import report
from tasks import cloud_tasks


def create_account_tasks(body: report.MCCRequest) -> int:
    return cloud_tasks.create_tasks(lambda x: f"{x['dataset']}-{x['report']}")(
        [
            {
                **y,  # type: ignore
                "report": body["report"],
                "dataset": body["dataset"],
                "table_suffix": body["table_suffix"],
            }
            for y in body["accounts"]
        ]
    )


def create_mcc_tasks(body: report.Request) -> int:
    return cloud_tasks.create_tasks(lambda x: f"{x['report']}")(
        [
            {
                **i,  # type: ignore
                "report": body["report"],
                "tasks": "account",
            }
            for i in report.mccs
        ]
    )
