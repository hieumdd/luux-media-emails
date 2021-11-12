from unittest.mock import Mock

import pytest

from main import main

ACCOUNTS = [
    "1897347778",
]
MODE = [
    "daily",
    "weekly",
]


def run(data: dict) -> dict:
    req = Mock(get_json=Mock(return_value=data), args=data)
    res = main(req)
    return res


@pytest.mark.parametrize(
    "account",
    ACCOUNTS,
)
@pytest.mark.parametrize(
    "mode",
    MODE,
)
def test_emails(account: str, mode: str):
    res = run(
        {
            "external_customer_id": account,
            "mode": mode,
        }
    )
    assert res["emails_sent"] > 0


@pytest.mark.parametrize(
    "mode",
    MODE,
)
def test_tasks(mode: str):
    res = run(
        {
            "tasks": mode,
        }
    )
    assert res["messages_sent"] > 0
