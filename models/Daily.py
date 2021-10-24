from models.metrics import Metric
from components import getter
from components import composer

class UnderspentAccounts(Metric):
    query = staticmethod(getter.underspent_account(1))
    compose_body = staticmethod(composer.underspent_account)

class UnderspentCampaigns(Metric):
    query = staticmethod(getter.underspent_campaigns(1))
    compose_body = staticmethod(composer.underspent_campaigns)


class Clicks(Metric):
    query = staticmethod(getter.metric_daily("Clicks"))
    compose_body = staticmethod(composer.metric_daily("Clicks"))


class Impressions(Metric):
    query = staticmethod(getter.metric_daily("Impressions"))
    compose_body = staticmethod(composer.metric_daily("Impressions"))



class Conversions(Metric):
    query = staticmethod(getter.metric_daily("Conversions"))
    compose_body = staticmethod(composer.metric_daily("Conversions"))


class CTR(Metric):
    query = staticmethod(getter.metric_daily("Ctr"))
    compose_body = staticmethod(composer.metric_daily("Ctr"))


class PotentialNegativeSearchTerms(Metric):
    query = staticmethod(getter.potential_negative_search_terms(1))
    compose_body = staticmethod(composer.potential_negative_search_terms)


class DisapprovedAds(Metric):
    query = staticmethod(getter.disapproved_ads(1))
    compose_body = staticmethod(composer.disapproved_ads)
