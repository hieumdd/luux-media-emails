from google.cloud import bigquery

from models.metrics.base import IMetric

BQ_CLIENT = bigquery.Client()


def get_customers(dataset: str, table_suffix: str) -> list[str]:
    results = BQ_CLIENT.query(
        f"SELECT DISTINCT ExternalCustomerId FROM {dataset}.AccountStats_{table_suffix}"
    ).result()
    rows = [dict(row.items()) for row in results]
    return [str(i["ExternalCustomerId"]) for i in rows]


def get_metric(
    dataset: str,
    table_suffix: str,
    external_customer_id: str,
    metric: IMetric,
) -> bigquery.QueryJob:
    job = BQ_CLIENT.query(metric["query"](dataset, table_suffix, external_customer_id))
    return job
