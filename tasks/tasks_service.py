from report import report
from tasks import cloud_tasks


def create_tasks_service(body):
    tasks = [
        {
            "report": body["report"],
            "dataset": mcc.dataset,
            "table_suffix": mcc.table_suffix,
            "receivers": mcc.receivers,
            "external_customer_id": account["external_customer_id"],
            "account_name": account["account_name"],
        }
        for mcc in report.mccs
        for account in mcc.accounts
    ]
    tasks_created = cloud_tasks.create_tasks(
        tasks,
        lambda x: f"{x['report']}-{x['external_customer_id']}",
    )
    return {
        "tasks": tasks_created,
    }
