from typing import Callable

from config import DATASET, TABLE_SUFFIX

def underspent_account(days: int) -> Callable:
    return lambda external_customer_id: f"""
    WITH base AS (
        SELECT SUM(bs.Cost) AS Cost, SUM(b.Amount) AS Amount,
        FROM {DATASET}.BudgetStats_{TABLE_SUFFIX} bs
        INNER JOIN {DATASET}.Budget_{TABLE_SUFFIX} b
            ON bs.BudgetId = b.BudgetId
        INNER JOIN {DATASET}.Campaign_{TABLE_SUFFIX} c
            ON bs.AssociatedCampaignId = c.CampaignId
        WHERE
            bs._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
            AND bs.ExternalCustomerId = {external_customer_id}
            AND b._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
            AND b.ExternalCustomerId = {external_customer_id}
            AND c._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
            AND c.ExternalCustomerId = {external_customer_id}
        )
    SELECT
        (Cost - Amount) / 100 AS underspent,
        (Cost - Amount) / Amount AS percentage
    FROM base
    """

def metric_daily(field: str) -> Callable:
    return (
        lambda external_customer_id: f"""
            WITH base AS (
                SELECT Date, SUM({field}) AS d0
                FROM {DATASET}.AccountStats_{TABLE_SUFFIX}
                WHERE
                    _DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -8 DAY)
                    AND ExternalCustomerId = {external_customer_id}
            GROUP BY 1
            ),
            base2 AS (
                SELECT
                    Date, d0,
                    LEAD(d0) OVER (ORDER BY Date DESC) AS d1,
                    (SELECT AVG(d0) FROM base) AS d7_avg
                FROM base
            )
            SELECT
                SAFE_DIVIDE(d0-d1,d1) as d1,
                SAFE_DIVIDE(d0-d7_avg,d7_avg) as d7_avg
            FROM base2
            WHERE
                Date = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY)
                -- AND (
                --     SAFE_DIVIDE(d0-d1,d1) < 0
                --     OR SAFE_DIVIDE(d0-d7_avg,d7_avg) < 0
                -- )
            """
    )




def underspent_campaigns(days: int) -> Callable:
    return (
        lambda external_customer_id: f"""
        WITH base AS (
            SELECT 
                c.CampaignName, 
                SUM(bs.Cost) AS Cost,
                SUM(b.Amount) AS Amount,
            FROM {DATASET}.BudgetStats_{TABLE_SUFFIX} bs
            INNER JOIN {DATASET}.Budget_{TABLE_SUFFIX} b
                ON bs.BudgetId = b.BudgetId
            INNER JOIN {DATASET}.Campaign_{TABLE_SUFFIX} c
            ON bs.AssociatedCampaignId = c.CampaignId
            WHERE
                bs._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                AND bs.ExternalCustomerId = {external_customer_id}
                AND b._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                AND b.ExternalCustomerId = {external_customer_id}
                AND c._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                AND c.ExternalCustomerId = {external_customer_id}
            GROUP BY 1
        ),
        base2 AS (
            SELECT CampaignName, (Cost - Amount) / Amount AS underspent
            FROM base
            WHERE Cost < Amount
        ),
        base3 AS (
            SELECT ARRAY_AGG(STRUCT(CampaignName AS campaigns, underspent)) AS campaigns
            FROM base2
        )
        SELECT * FROM base3 WHERE ARRAY_LENGTH(campaigns) > 0
        """
    )


def potential_negative_search_terms(days: int) -> Callable:
    return (
        lambda external_customer_id: f"""
        WITH base AS (
            SELECT
                Query AS query,
                SUM(Clicks) AS clicks,
                SUM(Conversions) AS conversions
            FROM {DATASET}.SearchQueryStats_{TABLE_SUFFIX}
            WHERE
                _DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                -- AND (Clicks > 50 AND Conversions = 0)
                AND ExternalCustomerId = {external_customer_id}
            GROUP BY 1
        ),
        base2 AS (
            SELECT ARRAY_AGG(STRUCT(query, clicks, conversions)) AS search_terms
            FROM base
            WHERE clicks > 50 AND conversions = 0
        )
        SELECT * FROM base2 WHERE ARRAY_LENGTH(search_terms) > 0
        """
    )


def disapproved_ads(days: int) -> Callable:
    return (
        lambda external_customer_id: f"""
        WITH base AS (
            SELECT ARRAY_AGG(DISTINCT CreativeId) AS creatives
            FROM {DATASET}.Ad_{TABLE_SUFFIX}
        WHERE _DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
            AND CombinedApprovalStatus = "disapproved"
            AND Status = "ENABLED"
            AND ExternalCustomerId = {external_customer_id}
        )
        SELECT * FROM base WHERE ARRAY_LENGTH(creatives) > 0    
        """
    )


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
