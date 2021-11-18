from typing import Callable

Getter = Callable[[str, str, str], str]


def metric_daily(field: str) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT Date, SUM({field}) AS d0
                FROM {dataset}.AccountStats_{table_suffix}
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
            ),
            base3 AS (
            SELECT
                SAFE_DIVIDE(d0-d1,d1) as d1,
                SAFE_DIVIDE(d0-d7_avg,d7_avg) as d7_avg
            FROM base2
            WHERE Date = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY)
            )
            SELECT * FROM base3
            """
    )


def metric_weekly(field: str) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
        WITH base AS (
            SELECT _DATA_DATE AS Date, SUM({field}) AS d0,
            FROM {dataset}.AccountStats_{table_suffix}
            WHERE ExternalCustomerId = {external_customer_id}
            GROUP BY 1 
        ),
        base2 AS (
            SELECT
                Date,
                d0,
                LEAD(d0, 7) OVER (ORDER BY Date DESC) AS d7,
                LEAD(d0, 30) OVER (ORDER BY Date DESC) AS d30
            FROM base
        ),
        base3 AS (
            SELECT
                SAFE_DIVIDE(SUM(d0)-SUM(d7),SUM(d7)) as d7,
                SAFE_DIVIDE(SUM(d0)-SUM(d30),SUM(d30)) as d30,
            FROM base2
            WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
        )
        SELECT * FROM base3
    """
    )


def underspent_accounts(days: int) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT 
                    SUM(bs.Cost) AS Cost,
                    SUM(b.Amount) AS Amount,
                FROM {dataset}.BudgetStats_{table_suffix} bs
                INNER JOIN {dataset}.Budget_{table_suffix} b
                    ON bs.BudgetId = b.BudgetId
                    AND bs._DATA_DATE = b._DATA_DATE
                WHERE
                    bs._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                    AND bs.ExternalCustomerId = {external_customer_id}
                    AND b._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                    AND b.ExternalCustomerId = {external_customer_id}
                ),
            base2 AS (
                SELECT
                    (Cost - Amount) / 100 AS underspent,
                    (Cost - Amount) / Amount AS percentage
                FROM base
            )
            SELECT * FROM base2 WHERE underspent IS NOT NULL
        """
    )


def underspent_budgets(days: int) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT 
                    c.CampaignName,
                    b.BudgetName,
                    SUM(bs.Cost) AS Cost,
                    SUM(b.Amount) AS Amount,
                FROM {dataset}.BudgetStats_{table_suffix} bs
                INNER JOIN {dataset}.Budget_{table_suffix} b
                    ON bs.BudgetId = b.BudgetId
                INNER JOIN {dataset}.Campaign_{table_suffix} c
                ON bs.AssociatedCampaignId = c.CampaignId
                WHERE
                    bs._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                    AND bs.ExternalCustomerId = {external_customer_id}
                    AND b._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                    AND b.ExternalCustomerId = {external_customer_id}
                    AND c._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                    AND c.ExternalCustomerId = {external_customer_id}
                GROUP BY 1, 2
            ),
            base2 AS (
                SELECT
                    BudgetName,
                    ARRAY_AGG(CampaignName) AS Campaigns,
                    (SUM(Cost) - AVG(Amount)) / AVG(Amount) AS underspent
                FROM base
                GROUP BY 1
                HAVING SUM(Cost) < AVG(Amount)
            ),
            base3 AS (
                SELECT
                    ARRAY_AGG(STRUCT(BudgetName,Campaigns,underspent)) AS budgets
                FROM base2
            )
            SELECT * FROM base3 WHERE ARRAY_LENGTH(budgets) > 0
        """
    )


def gdn_placements(days: int) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT p.DisplayName, SUM(pcs.Conversions) AS Conversions
            FROM {dataset}.PlacementConversionStats_{table_suffix} pcs
            INNER JOIN {dataset}.Placement_{table_suffix} p
                ON pcs.CampaignId = p.CampaignId
                AND pcs.AdGroupId = p.AdGroupId
            -- WHERE pcs._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
            -- AND p._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
            AND pcs.ExternalCustomerId = {external_customer_id}
            GROUP BY 1
            ),
            base2 AS (
                SELECT 
                    DisplayName, Conversions,
                    (SELECT AVG(Conversions) FROM base) AS avg_conversions,
            FROM base
            )
        SELECT COUNT(*) FROM base2
        WHERE (Conversions - avg_conversions) / avg_conversions > 0.5
    """
    )


def potential_negative_search_terms(days: int) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    Query AS query,
                    SUM(Clicks) AS clicks,
                    SUM(Conversions) AS conversions
                FROM {dataset}.SearchQueryStats_{table_suffix}
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


def disapproved_ads(days: int) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT ARRAY_AGG(DISTINCT CreativeId) AS creatives
                FROM {dataset}.Ad_{table_suffix}
            WHERE _DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                AND CombinedApprovalStatus = "disapproved"
                AND Status = "ENABLED"
                AND ExternalCustomerId = {external_customer_id}
            )
            SELECT * FROM base WHERE ARRAY_LENGTH(creatives) > 0    
        """
    )


def metric_sis() -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    _DATA_DATE AS Date,
                    AVG(SAFE_CAST(REPLACE(SearchImpressionShare, '%', '') AS NUMERIC)) AS SearchImpressionShare
                FROM {dataset}.AccountNonClickStats_{table_suffix}
                WHERE ExternalCustomerId = {external_customer_id}
                GROUP BY 1
            ),
            base2 AS (
                SELECT
                    Date, 
                    SearchImpressionShare AS d0,
                    LEAD(SearchImpressionShare, 7) OVER (ORDER BY Date DESC) AS d7,
                    LEAD(SearchImpressionShare, 30) OVER (ORDER BY Date DESC) AS d30,
                FROM base
            ),
            base3 AS (
                SELECT
                    SAFE_DIVIDE(SUM(d0)-SUM(d7),SUM(d7)) as d7,
                    SAFE_DIVIDE(SUM(d0)-SUM(d30),SUM(d30)) as d30,
                FROM base2
                WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                )
            SELECT * FROM base3
    """
    )


def metric_topsis() -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    _DATA_DATE AS Date,
                    AVG(SAFE_CAST(REPLACE(SearchTopImpressionShare, '%', '') AS NUMERIC)) AS SearchTopImpressionShare
                FROM {dataset}.CampaignCrossDeviceStats_{table_suffix}
                WHERE ExternalCustomerId = {external_customer_id}
                GROUP BY 1
            ),
            base2 AS (
                SELECT
                    Date, 
                    SearchTopImpressionShare AS d0,
                    LEAD(SearchTopImpressionShare, 7) OVER (ORDER BY Date DESC) AS d7,
                    LEAD(SearchTopImpressionShare, 30) OVER (ORDER BY Date DESC) AS d30,
                FROM base
            ),
            base3 AS (
                SELECT
                    SAFE_DIVIDE(SUM(d0)-SUM(d7),SUM(d7)) as d7,
                    SAFE_DIVIDE(SUM(d0)-SUM(d30),SUM(d30)) as d30,
                FROM base2
                WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                )
            SELECT * FROM base3
    """
    )


def metric_cpa(field: str) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    kbs.AdGroupId,
                    ag.AdGroupName,
                    kbs.CriterionId,
                    k.Criteria,
                    SUM(kbs.Cost) / 1000 AS Cost,
                    SUM(kbs.Conversions) AS Conversions,
                FROM {dataset}.KeywordBasicStats_{table_suffix} kbs
                INNER JOIN {dataset}.Keyword_{table_suffix} k
                    ON kbs.CampaignId = k.CampaignId
                    AND kbs.AdGroupId = k.AdGroupId
                    AND kbs.CriterionId = k.CriterionId
                    AND kbs._DATA_DATE = k._DATA_DATE
                INNER JOIN {dataset}.AdGroup_{table_suffix} ag
                    ON kbs.AdGroupId = ag.AdGroupId
                    AND kbs._DATA_DATE = ag._DATA_DATE
                WHERE kbs._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                AND kbs.ExternalCustomerId = {external_customer_id}
                GROUP BY 1, 2, 3, 4
            ),
            base2 AS (
                SELECT
                    {field},
                    SAFE_DIVIDE(SUM(Cost),SUM(Conversions)) AS cpa,
                FROM base
                GROUP BY 1
            ),
            base3 AS (
                SELECT
                    {field},
                    cpa,
                    (SELECT AVG(CPA) FROM base2) AS cpa_avg
                FROM base2
            )
            SELECT ARRAY_AGG({field}) AS values
            FROM base3
            WHERE (cpa - cpa_avg) > 0.5 * cpa_avg
        """
    )


def metric_performance(field: str) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    ags._DATA_DATE AS Date,
                    CampaignName,
                    AdGroupName,
                    AVG(Conversions) AS value
                FROM {dataset}.AdGroupStats_{table_suffix} ags
                INNER JOIN {dataset}.AdGroup_{table_suffix} ag
                    ON ags.CampaignId = ag.CampaignId
                    AND ags.AdGroupId = ag.AdGroupId
                    AND ags._DATA_DATE = ag._DATA_DATE
                INNER JOIN {dataset}.Campaign_{table_suffix} c
                    ON ags.CampaignId = c.CampaignId
                    AND ags._DATA_DATE = c._DATA_DATE
                WHERE ags.ExternalCustomerId = {external_customer_id}
                GROUP BY 1, 2, 3
            ),
            base2 AS (
                SELECT 
                    Date,
                    {field},
                    AVG(value) AS value
                FROM base
                GROUP BY 1, 2
            ),
            base3 AS (
                SELECT
                    Date,
                    {field},
                    value AS d0,
                    LEAD(value, 7) OVER (PARTITION BY {field} ORDER BY Date DESC) AS d7,
                    LEAD(value, 30) OVER (PARTITION BY {field} ORDER BY Date DESC) AS d30,
                FROM base2
            ),
            base4 AS (
                SELECT
                    {field},
                    AVG(d0) AS d0,
                    AVG(d7) AS d7,
                    AVG(d30) AS d30,
                FROM base3
                WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND d0 IS NOT NULL
                    AND d7 IS NOT NULL
                    AND d30 IS NOT NULL
                GROUP BY 1
            ),
            base5 AS (
                SELECT
                    ARRAY_AGG(
                    STRUCT(
                        {field} AS key,
                        (d0 - d7) / d7 AS d7,
                        (d0 - d30) / d30 AS d30
                    )
                ) AS value
                FROM base4
            )
            SELECT * FROM base5
            WHERE ARRAY_LENGTH(value) > 0
    """
    )
