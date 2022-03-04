from typing import Optional
import time

from google.cloud import bigquery

from db.bigquery import get_metric
from report.metrics.base import compose
from report.report import report_daily, report_weekly

reports = {
    "daily": report_daily,
    "weekly": report_weekly,
}


def poll(jobs: bigquery.LoadJob) -> None:
    undone_jobs = [job for job in jobs if not job.done()]
    if undone_jobs:
        time.sleep(5)
        return poll(jobs)


def build(
    dataset: str,
    table_suffix: str,
    external_customer_id: str,
    account_name: str,
    report: str,
) -> tuple[str, Optional[str]]:
    _report = reports[report]
    subject = f"Potential Issues With {account_name} on Google"
    prelude = f"<p>Please see the below potential issues when carrying out {_report['mode'].lower()} checks for {account_name} - {external_customer_id}</p>"
    jobs = [
        get_metric(dataset, table_suffix, external_customer_id, i)
        for i in _report["metrics"]
    ]
    poll(jobs)
    jobs_results = [i.result() for i in jobs]
    jobs_results = [
        [dict(row.items()) for row in job][0] if job.total_rows == 1 else None
        for job in [i.result() for i in jobs]
    ]
    body = "".join(
        [
            compose(metric, result)
            for metric, result in zip(_report["metrics"], jobs_results)
            if result
        ]
    )
    return (
        subject,
        f"<html><body>{prelude}{body}</body></html>" if body else None,
    )
