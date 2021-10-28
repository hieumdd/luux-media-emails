import time
from typing import Tuple

from google.cloud.bigquery import Client, LoadJob
from models import Daily, Weekly


def reports(client: Client, external_customer_id: str, mode="Daily") -> Tuple[str, str]:
    metrics = (
        [
            Daily.UnderspentAccounts,
            Daily.UnderspentCampaigns,
            Daily.Clicks,
            Daily.Impressions,
            Daily.Conversions,
            Daily.CTR,
            Daily.PotentialNegativeSearchTerms,
            # Daily.DisapprovedAds,
        ]
        if mode == "Daily"
        else [
            Weekly.UnderspentAccounts,
            Weekly.UnderspentCampaigns,
            Weekly.Clicks,
            Weekly.Impressions,
            Weekly.Conversions,
            Weekly.CTR,
            Weekly.CPC,
            Weekly.SIS,
            Weekly.TOPSIS,
            Weekly.PotentialNegativeSearchTerms,
            Weekly.CampaignPerformance,
            Weekly.AdGroupPerformance,
            Weekly.AdGroupCPA,
            Weekly.KeywordCPA,
            # Daily.DisapprovedAds,
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
