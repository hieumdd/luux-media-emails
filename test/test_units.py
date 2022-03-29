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
    # @pytest.fixture(
    #     params=[
    #         {
    #             "dataset": report.get_mcc()[0].dataset,
    #             "table_suffix": report.get_mcc()[0].table_suffix,
    #             "receivers": report.get_mcc()[0].receivers,
    #             "accounts": "123",  # type: ignore
    #         }
    #     ],
    # )
    # def body(self, request):
    #     return request.param

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
