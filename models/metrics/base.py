from typing import Callable, TypedDict

from models.getter import Getter


class IMetric(TypedDict):
    name: str
    query: Getter
    compose_body: Callable[[dict], str]


def compose(metric: IMetric, data: dict) -> str:
    body = metric["compose_body"](data)
    return f"<h3>{metric['name']}</h3>" + body if body else ""
