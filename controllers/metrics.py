from google.cloud.bigquery import Client, QueryJob

from models.metrics.base import IMetric


def get(
    client: Client,
    dataset: str,
    table_suffix: str,
    external_customer_id: str,
    metric: IMetric,
) -> QueryJob:
    job = client.query(metric["query"](dataset, table_suffix, external_customer_id))
    return job


def compose(metric: IMetric, data: dict) -> str:
    body = metric["compose_body"](data)
    return f"<h3>{metric['name']}</h3>" + body if body else ""
