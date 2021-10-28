from models.metrics import Metric
from components import getter
from components import composer


class UnderspentAccounts(Metric):
    name = "Budget Account"
    query = staticmethod(getter.underspent_account(7))
    compose_body = staticmethod(composer.underspent_account)


class UnderspentCampaigns(Metric):
    name = "Budget Campaigns"
    query = staticmethod(getter.underspent_campaigns(7))
    compose_body = staticmethod(composer.underspent_campaigns)


class Clicks(Metric):
    name = "Clicks"
    query = staticmethod(getter.metric_weekly("Clicks"))
    compose_body = staticmethod(composer.metric_weekly("Clicks"))


class Impressions(Metric):
    name = "Impressions"
    query = staticmethod(getter.metric_weekly("Impressions"))
    compose_body = staticmethod(composer.metric_weekly("Impressions"))


class Conversions(Metric):
    name = "Conversions"
    query = staticmethod(getter.metric_weekly("Conversions"))
    compose_body = staticmethod(composer.metric_weekly("Conversions"))


class CTR(Metric):
    name = "CTR"
    query = staticmethod(getter.metric_weekly("Ctr"))
    compose_body = staticmethod(composer.metric_weekly("CTR"))


class CPC(Metric):
    name = "CPC"
    query = staticmethod(getter.metric_weekly("AverageCpc"))
    compose_body = staticmethod(composer.metric_weekly("CPC"))


class SIS(Metric):
    name = "SIS"
    query = staticmethod(getter.metric_sis())
    compose_body = staticmethod(composer.metric_weekly("SIS"))


class TOPSIS(Metric):
    name = "TOPSIS"
    query = staticmethod(getter.metric_topsis())
    compose_body = staticmethod(composer.metric_weekly("TOPSIS"))


class GDNPlacements(Metric):
    name = "GDN Placements"
    query = staticmethod(getter.gdn_placements(7))
    compose_body = staticmethod(composer.gdn_placements)


class PotentialNegativeSearchTerms(Metric):
    name = "Potential Negative Search Terms"
    query = staticmethod(getter.potential_negative_search_terms(7))
    compose_body = staticmethod(composer.potential_negative_search_terms)


class DisapprovedAds(Metric):
    name = "Disapproved Ads"
    query = staticmethod(getter.disapproved_ads(7))
    compose_body = staticmethod(composer.disapproved_ads)
