from abc import ABCMeta, abstractmethod


class Metric(metaclass=ABCMeta):
    @property
    @staticmethod
    @abstractmethod
    def query(external_customer_id):
        pass

    def get(self, client, external_customer_id):
        def callback(job):
            rows = job.result()
            self.data = (
                [dict(row.items()) for row in rows][0] if rows.total_rows == 1 else None
            )

        query = self.query(external_customer_id)
        job = client.query(query)
        job.add_done_callback(callback)
        return job

    def compose(self):
        return f"<h3>{self.name}</h3>" + self.compose_body(self.data)

    def __init__(self):
        self.name = self.__class__.__name__
        self.data = None
