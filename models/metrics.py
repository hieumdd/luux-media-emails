from typing import Callable, TypedDict


class IMetric(TypedDict):
    name: str
    query: Callable[[str], str]
    compose_body: Callable[[dict], str]
