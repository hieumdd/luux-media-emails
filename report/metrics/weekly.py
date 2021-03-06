from report.metrics import getter
from report.metrics.base import IMetric
from report.metrics import formatter


underspent_accounts: IMetric = {
    "name": "Budget Account",
    "query": getter.underspent_accounts(7),
    "compose_body": formatter.underspent_accounts,
}


underspent_budgets: IMetric = {
    "name": "Budget Campaigns",
    "query": getter.underspent_budgets(7),
    "compose_body": formatter.underspent_budgets,
}


clicks: IMetric = {
    "name": "Clicks",
    "query": getter.metric_weekly_sum("Clicks"),
    "compose_body": formatter.metric_weekly("Clicks"),
}


impressions: IMetric = {
    "name": "Impressions",
    "query": getter.metric_weekly_sum("Impressions"),
    "compose_body": formatter.metric_weekly("Impressions"),
}


conversions: IMetric = {
    "name": "Conversions",
    "query": getter.metric_weekly_sum("Conversions"),
    "compose_body": formatter.metric_weekly("Conversions"),
}


ctr: IMetric = {
    "name": "CTR",
    "query": getter.metric_weekly_div("Clicks", "Impressions"),
    "compose_body": formatter.metric_weekly("CTR"),
}


cpc: IMetric = {
    "name": "CPC",
    "query": getter.metric_weekly_div("Cost", "Clicks"),
    "compose_body": formatter.metric_weekly("CPC"),
}


sis: IMetric = {
    "name": "SIS",
    "query": getter.metric_sis(),
    "compose_body": formatter.metric_weekly("SIS"),
}


topsis: IMetric = {
    "name": "TOPSIS",
    "query": getter.metric_topsis(),
    "compose_body": formatter.metric_weekly("TOPSIS"),
}


# gdn_placements: IMetric = {
#     "name": "GDN Placements",
#     "query": getter.gdn_placements(7),
#     "compose_body": composer.gdn_placements,
# }

potential_negative_search_terms: IMetric = {
    "name": "Potential Negative Search Terms",
    "query": getter.potential_negative_search_terms(7),
    "compose_body": formatter.potential_negative_search_terms,
}


disapproved_ads: IMetric = {
    "name": "Disapproved Ads",
    "query": getter.disapproved_ads(7),
    "compose_body": formatter.disapproved_ads,
}


campaign_performance: IMetric = {
    "name": "Campaign Performance",
    "query": getter.metric_performance("CampaignName"),
    "compose_body": formatter.metric_performance("Campaigns"),
}


ad_group_performance: IMetric = {
    "name": "Ad Group Performance",
    "query": getter.metric_performance("AdGroupName"),
    "compose_body": formatter.metric_performance("Ad Groups"),
}


ad_group_cpa: IMetric = {
    "name": "Ad Group CPA Alerts",
    "query": getter.ad_group_cpa(),
    "compose_body": formatter.metric_cpa("Ad Groups"),
}


keyword_cpa: IMetric = {
    "name": "Keyword CPA Alerts",
    "query": getter.keyword_cpa(),
    "compose_body": formatter.metric_cpa("Keywords"),
}
