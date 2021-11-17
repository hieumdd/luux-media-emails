import time
from typing import TypedDict, Tuple, Callable

from google.cloud.bigquery import Client, LoadJob
from models.metrics.base import IMetric
from models.metrics import daily, weekly


class IReport(TypedDict):
    mode: str
    metrics: list[IMetric]


report_daily: IReport = {
    "mode": "Daily",
    "metrics": [
        daily.underspent_accounts,
        daily.underspent_campaigns,
        daily.clicks,
        daily.impressions,
        daily.conversions,
        daily.ctr,
        daily.potential_negative_search_terms,
        # daily.disapproved_ads,
    ],
}

report_weekly: IReport = {
    "mode": "Weekly",
    "metrics": [
        weekly.underspent_accounts,
        weekly.underspent_campaigns,
        weekly.clicks,
        weekly.impressions,
        weekly.conversions,
        weekly.ctr,
        weekly.cpc,
        weekly.sis,
        weekly.topsis,
        weekly.potential_negative_search_terms,
        weekly.campaign_performance,
        weekly.ad_group_performance,
        weekly.ad_group_cpa,
        weekly.keyword_cpa,
        # weekly.disapproved_ads,
    ],
}


def reports(
    client: Client,
    external_customer_id: str,
    mode: str = "Daily",
) -> Callable[[], Tuple[str, str]]:
    metrics = (
        [
            daily.underspent_accounts,
            daily.underspent_campaigns,
            daily.clicks,
            daily.impressions,
            daily.conversions,
            daily.ctr,
            daily.potential_negative_search_terms,
            # daily.disapproved_ads,
        ]
        if mode == "daily"
        else [
            weekly.underspent_accounts,
            weekly.underspent_campaigns,
            weekly.clicks,
            weekly.impressions,
            weekly.conversions,
            weekly.ctr,
            weekly.cpc,
            weekly.sis,
            weekly.topsis,
            weekly.potential_negative_search_terms,
            weekly.campaign_performance,
            weekly.ad_group_performance,
            weekly.ad_group_cpa,
            weekly.keyword_cpa,
            # weekly.disapproved_ads,
        ]
    )

    def report() -> Tuple[str, str]:
        def poll(jobs: LoadJob):
            undone_jobs = [job for job in jobs if job.state != "DONE"]
            if undone_jobs:
                time.sleep(5)
                return poll(jobs)

        subject = f"Potential Issues With {external_customer_id} on Google"
        prelude = f"<p>Please see the below potential issues when carrying out {mode.lower()} checks for {external_customer_id}</p>"
        _metrics = [i() for i in metrics]
        jobs = [i.get(client, external_customer_id) for i in _metrics]
        poll(jobs)
        return (
            subject,
            f"<html><body>{prelude}{''.join([i.compose() for i in _metrics if i.data])}</body></html>",
        )

    return report
