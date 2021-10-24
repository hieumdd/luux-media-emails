from abc import ABCMeta, abstractmethod

from google.cloud.bigquery import Client, LoadJob


class Metric(metaclass=ABCMeta):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def query(external_customer_id: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def compose(data: dict) -> str:
        pass

    def get(self, client: Client, external_customer_id: str) -> LoadJob:
        def callback(job: LoadJob):
            rows = job.result()
            self.data = (
                [dict(row.items()) for row in rows][0] if rows.total_rows == 1 else None
            )

        query = self.query(external_customer_id)
        job = client.query(query)
        job.add_done_callback(callback)
        return job

    def compose(self) -> str:
        return f"<h3>{self.name}</h3>" + self.compose_body(self.data)

    def __init__(self):
        self.data = None
