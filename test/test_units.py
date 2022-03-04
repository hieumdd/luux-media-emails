from unittest.mock import Mock

import pytest

from main import main
from report import report_repo, report_service
from tasks import tasks_service
from db.bigquery import get_accounts


@pytest.fixture(
    params=report_repo.reports.keys(),
)
def report(request):
    return request.param


def run(data: dict) -> dict:
    return main(Mock(get_json=Mock(return_value=data), args=data))


class TestReport:
    accounts = [
        {"dataset": mcc[0], "table_suffix": mcc[1], **account}
        for mcc in [
            (
                i["dataset"],
                i["table_suffix"],
                get_accounts(
                    {
                        "dataset": i["dataset"],
                        "table_suffix": i["table_suffix"],
                    }
                ),
            )
            for i in tasks_service.MCC
        ]
        for account in mcc[2]
    ]

    @pytest.fixture(
        params=accounts,
        ids=[f"{i['dataset']}-{i['account_name']}" for i in accounts],
    )
    def body(self, request):
        return request.param

    def test_service(self, body, report):
        res = report_service.report_service({**body, "report": report})
        res

    def test_controller(self, body, report):
        res = run({**body, "report": report})
        assert res["email_sent"] >= 0


class TestTasks:
    @pytest.fixture(
        params=tasks_service.MCC,
        ids=[i["dataset"] for i in tasks_service.MCC],
    )
    def mcc(self, request):
        return request.param

    def test_create_account_tasks_service(self, mcc, report):
        res = tasks_service.create_account_tasks({**mcc, "report": report})
        res

    def test_create_account_tasks_controller(self, mcc, report):
        res = run({**mcc, "report": report, "tasks": "account"})
        res

    def test_create_mcc_tasks_service(self, report):
        res = tasks_service.create_mcc_tasks({"report": report, "tasks": "mcc"})
        res

    def test_create_mcc_tasks_controller(self, report):
        res = run({"report": report, "tasks": "mcc"})
        res
