from unittest.mock import Mock

import pytest

from main import main
from report import report_repo, report_service
from tasks import tasks_service
from db.bigquery import get_customers


@pytest.fixture(
    params=report_repo.reports.keys(),
)
def report(request):
    return request.param


def run(data: dict) -> dict:
    return main(Mock(get_json=Mock(return_value=data), args=data))


class TestReport:
    @pytest.fixture(
        params=[
            i
            for j in [
                get_customers(i["dataset"], i["table_suffix"])
                for i in tasks_service.MCC
            ]
            for i in j
        ],
        ids=[
            i["AccountDescriptiveName"]
            for j in [
                get_customers(i["dataset"], i["table_suffix"])
                for i in tasks_service.MCC
            ]
            for i in j
        ],
    )
    def body(self, request):
        return request.param

    def test_controller(self, body, report):
        res = run({**body, "report": report})
        assert res["emails_sent"] >= 0

    def test_service(self, body, report):
        res = report_service.report_service({**body, "report": report})
        res


class TestTasks:
    @pytest.mark.parametrize(
        "mcc",
        tasks_service.MCC,
        ids=[i["dataset"] for i in tasks_service.MCC],
    )
    def test_create_account_tasks_service(self, mcc, report):
        res = tasks_service.create_account_tasks({**mcc, "report": report})
        res

    def test_tasks(report):
        res = tasks_service.create_mcc_tasks({"report": report})
        res
