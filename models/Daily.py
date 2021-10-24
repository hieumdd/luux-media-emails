from models.metrics import Metric
from components import getter
from components import composer


class UnderspentAccounts(Metric):
    name = "Budget Account"
    query = staticmethod(getter.underspent_account(1))
    compose_body = staticmethod(composer.underspent_account)


class UnderspentCampaigns(Metric):
    name = "Budget Campaigns"
    query = staticmethod(getter.underspent_campaigns(1))
    compose_body = staticmethod(composer.underspent_campaigns)


class Clicks(Metric):
    name = "Clicks"
    query = staticmethod(getter.metric_daily("Clicks"))
    compose_body = staticmethod(composer.metric_daily("Clicks"))


class Impressions(Metric):
    name = "Impressions"
    query = staticmethod(getter.metric_daily("Impressions"))
    compose_body = staticmethod(composer.metric_daily("Impressions"))


class Conversions(Metric):
    name = "Conversions"
    query = staticmethod(getter.metric_daily("Conversions"))
    compose_body = staticmethod(composer.metric_daily("Conversions"))


class CTR(Metric):
    name = "CTR"
    query = staticmethod(getter.metric_daily("Ctr"))
    compose_body = staticmethod(composer.metric_daily("CTR"))


class PotentialNegativeSearchTerms(Metric):
    name = "Potential Negative Search Terms"
    query = staticmethod(getter.potential_negative_search_terms(1))
    compose_body = staticmethod(composer.potential_negative_search_terms)


class DisapprovedAds(Metric):
    name = "Disapproved Ads"
    query = staticmethod(getter.disapproved_ads(1))
    compose_body = staticmethod(composer.disapproved_ads)
