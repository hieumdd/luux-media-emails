from typing import TypedDict
from dataclasses import dataclass

from db.bigquery import get_accounts
from report.metrics.base import IMetric
from report.metrics import daily, weekly


@dataclass
class MCC:
    name: str
    dataset: str
    table_suffix: str
    receivers: list[str]
    accounts: list[dict[str, str]]


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
    ],
}

luux_media_accounts = get_accounts("GoogleAds", "3413321199")
multi_layer_accounts = get_accounts("GoogleAdsMultiLayer", "8228156051")

luux_media = MCC(
    name="LuuxMedia",
    dataset="GoogleAds",
    table_suffix="3413321199",
    receivers=[
        # "hieumdd@gmail.com",
        "analytics@luux-media.com",
    ],
    accounts=luux_media_accounts,
)

multi_layer = MCC(
    name="MultiLayer",
    dataset="GoogleAdsMultiLayer",
    table_suffix="8228156051",
    receivers=[
        # "hieumdd@gmail.com",
        "aaron@multi-layer-media.co.uk",
    ],
    accounts=[i for i in multi_layer_accounts if i not in luux_media_accounts],
)

mccs = [
    luux_media,
    multi_layer,
]
