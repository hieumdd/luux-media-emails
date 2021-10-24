from models.models import Metric
from components.query import metric_daily

def metric_weekly(table, field):
    return f"""
        WITH base AS (
            SELECT Date, SUM({field}) AS d0,
            FROM {table}
            WHERE _DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -31 DAY)
            GROUP BY 1
        ),
        base2 AS (
            SELECT Date, d0,
                LEAD(d0, 7) OVER (ORDER BY Date DESC) AS d7,
                LEAD(d0, 30) OVER (ORDER BY Date DESC) AS d30
            FROM base
            ORDER BY 1 DESC LIMIT 7
        )
        SELECT
            MAX(Date) AS Date,
            SUM(d0) AS d0,
            SUM(d7) AS d7,
            SUM(d30) AS d30
        FROM base2
        """

class Clicks(Metric):
    query = lambda self: metric_weekly(self.table, "Clicks")


class Impressions(Metric):
    query = lambda self: metric_weekly(self.table, "Impressions")


class Conversions(Metric):
    query = lambda self: metric_weekly(self.table, "Conversions")


class CTR(Metric):
    query = lambda self: metric_weekly(self.table, "Ctr")


class DailyPotentialNegativeSearchTerms(Metric):
    query = (
        lambda self: f"""
            SELECT
                ARRAY_AGG(DISTINCT Query) AS values,
            FROM
                {self.table}
            WHERE
                _DATA_DATE = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY)
                AND (
                    Clicks > 50
                    AND Conversions = 0
                )
            """
    )
