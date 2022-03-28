from typing import TypedDict


class AccountTask(TypedDict):
    dataset: str
    table_suffix: str


class MCCTask(TypedDict):
    dataset: str
    table_suffix: str
