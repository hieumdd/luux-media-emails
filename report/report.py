from typing import TypedDict

from report.metrics.base import IMetric
from report.metrics import daily, weekly


class MCC(TypedDict):
    dataset: str
    table_suffix: str


class Request(TypedDict):
    report: str


class Account(MCC):
    external_customer_id: str
    account_name: str


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
