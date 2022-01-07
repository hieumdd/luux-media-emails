from google.cloud import bigquery

from models.metrics.base import IMetric

BQ_CLIENT = bigquery.Client()


def get_customers(dataset: str, table_suffix: str) -> list[dict[str, str]]:
    results = BQ_CLIENT.query(
        f"""SELECT
            ExternalCustomerId,
            AccountDescriptiveName,
            FROM {dataset}.Customer_{table_suffix}
            WHERE _DATA_DATE = _LATEST_DATE
        """
    ).result()
    rows = [dict(row.items()) for row in results]
    return [
        {
            "ExternalCustomerId": str(i["ExternalCustomerId"]),
            "AccountDescriptiveName": i["AccountDescriptiveName"],
        }
        for i in rows
    ]


def get_metric(
    dataset: str,
    table_suffix: str,
    external_customer_id: str,
    metric: IMetric,
) -> bigquery.QueryJob:
    job = BQ_CLIENT.query(metric["query"](dataset, table_suffix, external_customer_id))
    return job
