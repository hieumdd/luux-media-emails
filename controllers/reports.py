from typing import Optional
import time

from google.cloud import bigquery

from controllers.metrics import get, compose
from models.reports import IReport, report_daily, report_weekly


def report_factory(mode: str = "daily") -> IReport:
    if mode == "daily":
        return report_daily
    else:
        return report_weekly


def poll(jobs: bigquery.LoadJob) -> None:
    undone_jobs = [job for job in jobs if not job.done()]
    if undone_jobs:
        time.sleep(5)
        return poll(jobs)


def build_report(
    client: bigquery.Client,
    dataset: str,
    table_suffix: str,
    external_customer_id: str,
    report: IReport,
) -> tuple[str, Optional[str]]:
    subject = f"Potential Issues With {external_customer_id} on Google"
    prelude = f"<p>Please see the below potential issues when carrying out {report['mode'].lower()} checks for {external_customer_id}</p>"
    jobs = [
        get(client, dataset, table_suffix, external_customer_id, i)
        for i in report["metrics"]
    ]
    poll(jobs)
    jobs_results = [
        [dict(row.items()) for row in job.result()][0]
        if job.result().total_rows == 1
        else None
        for job in jobs
    ]
    body = [
        compose(metric, result)
        for metric, result in zip(report["metrics"], jobs_results)
        if result
    ]
    return (
        subject,
        f"<html><body>{prelude}{''.join(body)}</body></html>" if body else None,
    )
