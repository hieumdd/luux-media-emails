from typing import TypedDict

from db.bigquery import get_accounts
from report.metrics.base import IMetric
from report.metrics import daily, weekly


class _MCC(TypedDict):
    name: str
    dataset: str
    table_suffix: str
    receivers: list[str]


class Account(_MCC):
    external_customer_id: str
    account_name: str


class MCC(_MCC):
    accounts: list[Account]


class Request(TypedDict):
    report: str


class AccountRequest(Account, Request):
    pass


class MCCRequest(MCC, Request):
    pass


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

luux_media: MCC = {
    "name": "LuuxMedia",
    "dataset": "GoogleAds",
    "table_suffix": "3413321199",
    "accounts": luux_media_accounts,  # type: ignore
    "receives": [
        "hieumdd@gmail.com",
        # "analytics@luux-media.com",
    ],
}

multi_layer: MCC = {
    "name": "MultiLayer",
    "dataset": "GoogleAdsMultiLayer",
    "table_suffix": "8228156051",
    "accounts": [
        i  # type: ignore
        for i in get_accounts("GoogleAdsMultiLayer", "8228156051")
        if i not in luux_media_accounts
    ],
    "receviers": [
        "hieumdd@gmail.com",
        # "analytics@luux-media.com",
    ],
}

mccs = [
    luux_media,
    multi_layer,
]
