from typing import Callable, Union


def format_scalar(number: Union[float, int]) -> str:
    return f"{number:,}"


def format_percentage(number: Union[float, int]) -> str:
    return f"{number:.2%}"


def metric_daily(name: str) -> Callable:
    def compose(data: dict) -> str:
        return f"""
        <p>{name} were {format_percentage(data["d1"])} compared to the previous day</p>
        <p>{name} were {format_percentage(data["d7_avg"])} compared to the previous 7 day average</p>
        """

    return compose


def metric_weekly(name: str) -> Callable:
    def compose(data: dict) -> str:
        return f"""
        <p>{name} were {format_percentage(data["d7"])} compared to the previous week</p>
        <p>{name} were {format_percentage(data["d30"])} compared to viewing MOM performance</p>
        """

    return compose


def underspent_account(data: dict) -> str:
    return f"""
    <p>The account underspent by {format_percentage(data['percentage'])} ({format_scalar(data['underspent'])})
    """


def underspent_campaigns(data: dict) -> str:
    lines = [
        f"<li>{i['campaigns']} - {format_percentage(i['underspent'])} underspent</li>"
        for i in data["campaigns"]
    ]
    return f"""
    <p>The campaigns that underspent are listed below</p>
    <ul>{''.join(lines)}</ul>
    """


def gdn_placements(data: dict) -> str:
    return f"""
    <p>{data['cnt']} placement generated more than 50% of your GDN conversions</p>
    """


def potential_negative_search_terms(data: dict) -> str:
    lines = [
        f"<li>{i['query']} - {i['clicks']} clicks - {i['conversions']} conversions</li>"
        for i in data["search_terms"]
    ]
    return f"""
    <p>The following search terms generated more than 50 clicks but no conversions:</p>
    <ul>{''.join(lines)}</ul>
    """


def disapproved_ads(data: dict) -> str:
    lines = [f"<li>{i}</li>" for i in data["creatives"]]
    return f"""
    <p>The following ads have been newly disapproved:</p>
    <ul>{''.join(lines)}</ul>
    """


def metric_cpa(field: str) -> Callable:
    def compose(data: dict) -> str:
        lines = [f"<li>{i}</li>" for i in data["values"]]
        return f"""
        <p>The following {field} have a CPA that is 50% or more higher than the account average:</p>
        <ul>{''.join(lines)}</ul>
        """

    return compose
