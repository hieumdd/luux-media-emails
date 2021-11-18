from unittest.mock import Mock

import pytest

from main import main, BQ_CLIENT, DATASET, TABLE_SUFFIX
from controllers.tasks import get_customers

MODE = [
    "daily",
    "weekly",
]


def run(data: dict) -> dict:
    return main(Mock(get_json=Mock(return_value=data), args=data))


@pytest.mark.parametrize(
    "account",
    get_customers(BQ_CLIENT, DATASET, TABLE_SUFFIX),
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
    assert res["emails_sent"] >= 0


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
