from typing import TypedDict

from models.metrics.base import IMetric
from models.metrics import daily, weekly


class IReport(TypedDict):
    mode: str
    metrics: list[IMetric]


report_daily: IReport = {
    "mode": "Daily",
    "metrics": [
        daily.underspent_accounts,
        daily.underspent_budgets,
        daily.clicks,
        daily.impressions,
        daily.conversions,
        daily.ctr,
        daily.potential_negative_search_terms,
        # daily.disapproved_ads, # Removed
    ],
}

report_weekly: IReport = {
    "mode": "Weekly",
    "metrics": [
        weekly.underspent_accounts,
        weekly.underspent_budgets,
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
        # weekly.disapproved_ads, # Removed
    ],
}
