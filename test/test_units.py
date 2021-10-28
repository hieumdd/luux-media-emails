from unittest.mock import Mock

import pytest

from main import main

ACCOUNTS = [
    "8735453121",
]
MODE = [
    "Daily",
    "Weekly",
]


def run(data):
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
def test_emails(account, mode):
    res = run(
        {
            "external_customer_id": account,
            "mode": mode,
        }
    )
    assert res["emails_sent"] > 0
