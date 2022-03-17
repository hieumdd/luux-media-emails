from compose import compose

from report import report, report_repo
from mail import mail_service


SENDER = "siddhantmehandru.developer@gmail.com"


def report_service(data: report.AccountRequest) -> list[str]:
    return compose(
        mail_service.send(SENDER, data.get("receivers", [])),
        report_repo.build,
    )(**data)
