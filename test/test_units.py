from unittest.mock import Mock

import pytest

from main import main, DATASET, TABLE_SUFFIX
from controllers.tasks import get_customers

MODE = [
    "daily",
    "weekly",
]


def run(data: dict) -> dict:
    return main(Mock(get_json=Mock(return_value=data), args=data))


@pytest.mark.parametrize(
    "account",
    get_customers(DATASET, TABLE_SUFFIX),
    ids=[i["AccountDescriptiveName"] for i in get_customers(DATASET, TABLE_SUFFIX)],
)
@pytest.mark.parametrize(
    "mode",
    MODE,
)
def test_emails(account: dict[str, str], mode: str):
    res = run(
        {
            "external_customer_id": account["ExternalCustomerId"],
            "account_name": account["AccountDescriptiveName"],
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
