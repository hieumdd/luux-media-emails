from models.metrics import IMetric
from components import getter, composer

underspent_accounts: IMetric = {
    "name": "Budget Account",
    "query": getter.underspent_accounts(1),
    "compose_body": composer.underspent_accounts,
}


underspent_campaigns: IMetric = {
    "name": "Budget Campaigns",
    "query": getter.underspent_campaigns(1),
    "compose_body": composer.underspent_campaigns,
}

clicks: IMetric = {
    "name": "Clicks",
    "query": getter.metric_daily("Clicks"),
    "compose_body": composer.metric_daily("Clicks"),
}

impressions: IMetric = {
    "name": "Impressions",
    "query": getter.metric_daily("Impressions"),
    "compose_body": composer.metric_daily("Impressions"),
}

conversions: IMetric = {
    "name": "Conversions",
    "query": getter.metric_daily("Conversions"),
    "compose_body": composer.metric_daily("Conversions"),
}

ctr: IMetric = {
    "name": "CTR",
    "query": getter.metric_daily("Ctr"),
    "compose_body": composer.metric_daily("CTR"),
}

gdn_placements: IMetric = {
    "name": "GDN Placements",
    "query": getter.gdn_placements(1),
    "compose_body": composer.gdn_placements,
}

potential_negative_search_terms: IMetric = {
    "name": "Potential Negative Search Terms",
    "query": getter.potential_negative_search_terms(1),
    "compose_body": composer.potential_negative_search_terms,
}

disapproved_ads: IMetric = {
    "name": "Disapproved Ads",
    "query": getter.disapproved_ads(1),
    "compose_body": composer.disapproved_ads,
}
