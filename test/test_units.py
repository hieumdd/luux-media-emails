from unittest.mock import Mock

import pytest

from main import main
from report import report, report_repo, report_service
from tasks import tasks_service


@pytest.fixture(
    params=report_repo.reports.keys(),
)
def report_(request):
    return request.param


def run(data: dict) -> dict:
    return main(Mock(get_json=Mock(return_value=data), args=data))


class TestReport:
    accounts = [
        {
            "dataset": mcc["dataset"],
            "table_suffix": mcc["table_suffix"],
            "receivers": mcc["receivers"],
            **account,  # type: ignore
        }
        for mcc in report.mccs
        for account in mcc["accounts"]  # type: ignore
    ]

    @pytest.fixture(
        params=accounts,
        ids=[f"{i['dataset']}-{i['account_name']}" for i in accounts],
    )
    def body(self, request):
        return request.param

    def test_service(self, body, report_):
        res = report_service.report_service({**body, "report": report_})
        res

    def test_controller(self, body, report_):
        res = run({**body, "report": report_})
        assert len(res["email_sent"]) >= 0


class TestTasks:
    def test_service(self, report_):
        res = tasks_service.create_tasks_service({"report": report_, "tasks": "mcc"})
        res

    def test_controller(self, report_):
        res = run({"report": report_, "tasks": "mcc"})
        res
