from models.metrics import IMetric


def get(client, dataset, table_suffix, external_customer_id, metric: IMetric) -> str:
    query = metric["query"](dataset, table_suffix, external_customer_id)
    job = client.query(query)
    return job


def compose(metric: IMetric, data: dict) -> str:
    body = metric["compose_body"](data)
    return f"<h3>{metric['name']}</h3>" + body if body else ""
