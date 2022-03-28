from report.metrics import getter
from report.metrics.base import IMetric
from report.metrics import formatter

underspent_accounts: IMetric = {
    "name": "Budget Account",
    "query": getter.underspent_accounts(1),
    "compose_body": formatter.underspent_accounts,
}


underspent_budgets: IMetric = {
    "name": "Budget Campaigns",
    "query": getter.underspent_budgets(1),
    "compose_body": formatter.underspent_budgets,
}

clicks: IMetric = {
    "name": "Clicks",
    "query": getter.metric_daily_sum("Clicks"),
    "compose_body": formatter.metric_daily("Clicks"),
}

impressions: IMetric = {
    "name": "Impressions",
    "query": getter.metric_daily_sum("Impressions"),
    "compose_body": formatter.metric_daily("Impressions"),
}

conversions: IMetric = {
    "name": "Conversions",
    "query": getter.metric_daily_sum("Conversions"),
    "compose_body": formatter.metric_daily("Conversions"),
}

ctr: IMetric = {
    "name": "CTR",
    "query": getter.metric_daily_div("Clicks", "Impressions"),
    "compose_body": formatter.metric_daily("CTR"),
}

# gdn_placements: IMetric = {
#     "name": "GDN Placements",
#     "query": getter.gdn_placements(1),
#     "compose_body": composer.gdn_placements,
# }

potential_negative_search_terms: IMetric = {
    "name": "Potential Negative Search Terms",
    "query": getter.potential_negative_search_terms(1),
    "compose_body": formatter.potential_negative_search_terms,
}

disapproved_ads: IMetric = {
    "name": "Disapproved Ads",
    "query": getter.disapproved_ads(1),
    "compose_body": formatter.disapproved_ads,
}
