from typing import Callable, Union

MetricComposer = Callable[[dict], str]


def format_scalar(number: Union[float, int]) -> str:
    return f"{number:,.2f}"


def format_percentage(number: Union[float, int]) -> str:
    return f"{number:.2%}"


def metric_daily(name: str) -> MetricComposer:
    def compose(data: dict) -> str:
        if not data["d1"] or not data["d7_avg"]:
            return ""
        else:
            d1 = (
                f"<p>{name} were {format_percentage(data['d1'])} compared to the previous day</p>"
                if data["d1"] < 0
                else ""
            )
            d7_avg = (
                f"<p>{name} were {format_percentage(data['d7_avg'])} compared to the previous 7 day average</p>"
                if data["d7_avg"] < 0
                else ""
            )
            return d1 + d7_avg

    return compose


def metric_weekly(name: str) -> MetricComposer:
    def compose(data: dict) -> str:
        dw = (
            f"<p>{name} were {format_percentage(data['dw'])} compared to the previous week</p>"
            if data["dw"] < 0
            else ""
        )
        dmom = (
            f"<p>{name} were {format_percentage(data['dmom'])} compared to viewing MOM performance</p>"
            if data["dmom"] < 0
            else ""
        )
        return dw + dmom

    return compose


def underspent_accounts(data: dict) -> str:
    return f"""
    <p>The account underspent by {format_percentage(data['percentage'])} ({format_scalar(data['underspent'])})
    """


def underspent_budgets(data: dict) -> str:
    lines = [
        "<li>"
        + f"{budget['BudgetName']} - {format_percentage(budget['underspent'])} underspent"
        + "<ul>"
        + "".join([f"<li>{campaign}</li>" for campaign in budget["Campaigns"]])
        + "</ul>"
        + "</li>"
        for budget in data["budgets"]
    ]
    return f"""
    <p>The budgets that underspent are listed below</p>
    <ul>{''.join(lines)}</ul>
    """


def gdn_placements(data: dict) -> str:
    return f"<p>{data['cnt']} placement generated more than 50% of your GDN conversions</p>"


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


def metric_cpa(field: str) -> MetricComposer:
    def compose(data: dict) -> str:
        lines = [f"<li>{i}</li>" for i in data["values"]]
        return f"""
        <p>The following {field} have a CPA that is 30% or more higher than the account average of {format_scalar(data['avg'])}:</p>
        <ul>{''.join(lines)}</ul>
        """

    return compose


def metric_performance(field: str) -> MetricComposer:
    def compose(data: dict) -> str:
        week_lines = [f"<li>{i['key']}</li>" for i in data["value"] if i["d7"] < 0]
        month_lines = [f"<li>{i['key']}</li>" for i in data["value"] if i["d30"] < 0]
        return f"""
        <p>Performance on the following {field} has reduced WOW:</p>
        <ul>{''.join(week_lines)}</ul>
        <p>Performance on the following {field} has reduced MOM:</p>
        <ul>{''.join(month_lines)}</ul>
        """

    return compose
