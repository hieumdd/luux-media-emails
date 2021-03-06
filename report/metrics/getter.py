from typing import Callable

Getter = Callable[[str, str, str], str]


def metric_daily_sum(field: str) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    RawDate AS Date,
                    SUM({field}) AS d0,
                FROM (
                    SELECT * FROM (
                        SELECT * FROM
                        UNNEST(
                            GENERATE_DATE_ARRAY(
                                DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                                CURRENT_DATE(),
                                INTERVAL 1 DAY
                            )
                        ) AS RawDate
                    ) _cal
                    LEFT JOIN (
                        SELECT * FROM
                        {dataset}.AccountBasicStats_{table_suffix}
                        WHERE ExternalCustomerId = {external_customer_id}
                    ) b
                    ON _cal.RawDate = b._DATA_DATE
                )
                WHERE
                    RawDate >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND RawDate <> CURRENT_DATE()
                GROUP BY 1
            ),
            base2 AS (
                SELECT
                    Date, d0,
                    LEAD(d0) OVER (ORDER BY Date DESC) AS d1,
                    _avg.d7_avg,
                FROM base
                CROSS JOIN (
                        SELECT AVG(d0) as d7_avg FROM base
                        WHERE Date <> DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY)
                    ) AS _avg
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


def metric_daily_div(nume: str, denom: str) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    RawDate AS Date,
                    SUM({nume}) AS nume0,
                    SUM(NULLIF({denom}, 0)) AS denom0,
                FROM (
                    SELECT * FROM (
                        SELECT * FROM
                        UNNEST(
                            GENERATE_DATE_ARRAY(
                                DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                                CURRENT_DATE(),
                                INTERVAL 1 DAY
                            )
                        ) AS RawDate
                    ) _cal
                    LEFT JOIN (
                        SELECT * FROM
                        {dataset}.AccountBasicStats_{table_suffix}
                        WHERE ExternalCustomerId = {external_customer_id}
                    ) b
                    ON _cal.RawDate = b._DATA_DATE
                )
                WHERE
                    RawDate >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND RawDate <> CURRENT_DATE()
                GROUP BY 1
            ),
            base2 AS (
                SELECT
                    Date,
                    nume0,
                    denom0,
                    LEAD(nume0) OVER (ORDER BY Date DESC) AS nume1,
                    LEAD(denom0) OVER (ORDER BY Date DESC) AS denom1,
                    _avg.nume7,
                    _avg.denom7,
                FROM base
                CROSS JOIN (
                    SELECT
                        SUM(nume0) AS nume7,
                        SUM(denom0) AS denom7,
                    FROM base
                    WHERE Date <> DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY)
                ) AS _avg
            ),
            base3 AS (
                SELECT
                    SAFE_DIVIDE(
                        (SUM(nume0) / SUM(NULLIF(denom0, 0))) - (SUM(nume1) / SUM(NULLIF(denom1, 0))),
                        (SUM(nume1) / SUM(NULLIF(denom1, 0)))
                    ) as d1,
                    SAFE_DIVIDE(
                        (SUM(nume0) / SUM(NULLIF(denom0, 0))) - (SUM(nume7) / SUM(NULLIF(denom7, 0))),
                        (SUM(nume7) / SUM(NULLIF(denom7, 0)))
                    ) as d7_avg
                FROM base2
                WHERE Date = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY)
            )
            SELECT * FROM base3
            """
    )


def metric_weekly_sum(field: str) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
        WITH base AS (
            SELECT
                RawDate AS Date,
                DATE_TRUNC(RawDate, Month) AS Month,
                EXTRACT(DAY FROM RawDate) AS Day,
                SUM({field}) AS d0,
            FROM (
                SELECT * FROM (
                    SELECT * FROM
                    UNNEST(
                        GENERATE_DATE_ARRAY(
                            DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                            CURRENT_DATE(),
                            INTERVAL 1 DAY
                        )
                    ) AS RawDate
                ) _cal
                LEFT JOIN (
                    SELECT * FROM
                    {dataset}.AccountBasicStats_{table_suffix}
                    WHERE ExternalCustomerId = {external_customer_id}
                ) b
                ON _cal.RawDate = b._DATA_DATE
            )
            GROUP BY 1, 2
        ),
        base2 AS (
            SELECT
                Date,
                Month,
                d0,
                LEAD(d0, 7) OVER (ORDER BY Date DESC) AS d7,
                LEAD(d0, 1) OVER (PARTITION BY Day ORDER BY Month DESC) AS d_mom,
            FROM base
        ),
        base3 AS (
            SELECT
                (
                    SELECT SUM(d0) FROM base2
                    WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND Date <> CURRENT_DATE()
                ) AS d7,
                (
                    SELECT SUM(d7) FROM base2
                    WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND Date <> CURRENT_DATE()
                ) AS d14,
                (
                    SELECT SUM(d0) FROM base2
                    WHERE Date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                    AND Date <> CURRENT_DATE()
                ) AS dtm,
                (
                    SELECT SUM(d_mom) FROM base2
                    WHERE Date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                    AND Date <> CURRENT_DATE()
                ) AS dlm,
        )
        SELECT
            SAFE_DIVIDE(d7-d14,d14) AS dw,
            SAFE_DIVIDE(dtm-dlm, dlm) AS dmom,
        FROM base3
        """
    )


def metric_weekly_div(nume: str, denom: str) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
        WITH base AS (
            SELECT
                _DATA_DATE AS Date,
                DATE_TRUNC(Date, Month) AS Month,
                EXTRACT(DAY FROM _DATA_DATE) AS Day,
                SUM({nume}) AS nume0,
                SUM(NULLIF({denom}, 0)) AS denom0,
            FROM (
                SELECT * FROM (
                    SELECT * FROM
                    UNNEST(
                        GENERATE_DATE_ARRAY(
                            DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                            CURRENT_DATE(),
                            INTERVAL 1 DAY
                        )
                    ) AS RawDate
                ) _cal
                LEFT JOIN (
                    SELECT * FROM
                    {dataset}.AccountBasicStats_{table_suffix}
                    WHERE ExternalCustomerId = {external_customer_id}
                ) b
                ON _cal.RawDate = b._DATA_DATE
            )
            WHERE ExternalCustomerId = {external_customer_id}
            GROUP BY 1, 2
        ),
        base2 AS (
            SELECT
                Date,
                Month,
                nume0,
                denom0,
                LEAD(nume0, 7) OVER (ORDER BY Date DESC) AS nume7,
                LEAD(denom0, 7) OVER (ORDER BY Date DESC) AS denom7,
                LEAD(nume0, 1) OVER (PARTITION BY Day ORDER BY Month DESC) AS nume_mom,
                LEAD(denom0, 1) OVER (PARTITION BY Day ORDER BY Month DESC) AS denom_mom,
            FROM base
        ),
        base3 AS (
            SELECT
                (
                    SELECT SUM(nume0) / SUM(NULLIF(denom0, 0)) FROM base2
                    WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND Date <> CURRENT_DATE()
                ) AS d7,
                (
                    SELECT SUM(nume7) / SUM(NULLIF(denom7, 0)) FROM base2
                    WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND Date <> CURRENT_DATE()
                ) AS d14,
                (
                    SELECT SUM(nume0) / SUM(NULLIF(denom0, 0)) FROM base2
                    WHERE Date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                    AND Date <> CURRENT_DATE()
                ) AS dtm,
                (
                    SELECT SUM(nume_mom) / SUM(NULLIF(denom_mom, 0)) FROM base2
                    WHERE Date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                    AND Date <> CURRENT_DATE()
                ) AS dlm,
        )
        SELECT
            SAFE_DIVIDE(d7-d14,d14) AS dw,
            SAFE_DIVIDE(dtm-dlm, dlm) AS dmom,
        FROM base3
        """
    )


def underspent_accounts(days: int) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT 
                    bs._DATA_DATE AS Date,
                    c.CampaignName,
                    b.BudgetName,
                    SUM(bs.Cost) / 1000000 AS Cost,
                    AVG(b.Amount) / 1000000 AS Amount,
                FROM {dataset}.BudgetStats_{table_suffix} bs
                INNER JOIN {dataset}.Budget_{table_suffix} b
                    ON bs.BudgetId = b.BudgetId
                INNER JOIN {dataset}.Campaign_{table_suffix} c
                ON bs.AssociatedCampaignId = c.CampaignId
                WHERE
                    bs._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                    AND bs._DATA_DATE <> CURRENT_DATE()
                    AND bs.ExternalCustomerId = {external_customer_id}
                    AND b._DATA_DATE = b._LATEST_DATE
                    AND b.ExternalCustomerId = {external_customer_id}
                    AND c._DATA_DATE = c._LATEST_DATE
                    AND c.ExternalCustomerId = {external_customer_id}
                GROUP BY 1, 2, 3
            ),
            base2 AS (
                SELECT
                    Date,
                    BudgetName,
                    ARRAY_AGG(CampaignName) AS Campaigns,
                    SUM(Cost) AS Cost,
                    AVG(Amount) AS Amount,
                FROM base
                GROUP BY 1, 2
            ),
            base3 AS (
                SELECT
                    BudgetName,
                    ANY_VALUE(Campaigns) AS Campaigns,
                    SUM(Cost) AS Cost,
                    SUM(Amount) AS Amount,
                    (SUM(Cost) - AVG(Amount)) / AVG(Amount) AS underspent
                FROM base2
                GROUP BY 1
                HAVING Cost < Amount
            )
            SELECT
                SUM(Cost) - SUM(Amount) AS underspent,
                SAFE_DIVIDE(SUM(Cost) - SUM(Amount), SUM(Amount)) AS percentage,
            FROM base3
        """
    )


def underspent_budgets(days: int) -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT 
                    bs._DATA_DATE AS Date,
                    c.CampaignName,
                    b.BudgetName,
                    SUM(bs.Cost) / 1000000 AS Cost,
                    AVG(b.Amount) / 1000000 AS Amount,
                FROM {dataset}.BudgetStats_{table_suffix} bs
                INNER JOIN {dataset}.Budget_{table_suffix} b
                    ON bs.BudgetId = b.BudgetId
                INNER JOIN {dataset}.Campaign_{table_suffix} c
                ON bs.AssociatedCampaignId = c.CampaignId
                WHERE
                    bs._DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                    AND bs._DATA_DATE <> CURRENT_DATE()
                    AND bs.ExternalCustomerId = {external_customer_id}
                    AND b._DATA_DATE = b._LATEST_DATE
                    AND b.ExternalCustomerId = {external_customer_id}
                    AND c._DATA_DATE = c._LATEST_DATE
                    AND c.ExternalCustomerId = {external_customer_id}
                GROUP BY 1, 2, 3
            ),
            base2 AS (
                SELECT
                    Date,
                    BudgetName,
                    ARRAY_AGG(CampaignName) AS Campaigns,
                    SUM(Cost) AS Cost,
                    AVG(Amount) AS Amount,
                FROM base
                GROUP BY 1, 2
            ),
            base3 AS (
                SELECT
                    BudgetName,
                    ANY_VALUE(Campaigns) AS Campaigns,
                    SUM(Cost),
                    SUM(Amount),
                    (SUM(Cost) - AVG(Amount)) / AVG(Amount) AS underspent
                FROM base2
                GROUP BY 1
                HAVING SUM(Cost) < AVG(Amount)
            ),
            base4 AS (
                SELECT
                    ARRAY_AGG(STRUCT(BudgetName,Campaigns,underspent)) AS budgets
                FROM base3
            )
            SELECT * FROM base4 WHERE ARRAY_LENGTH(budgets) > 0
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
                    AND _DATA_DATE <> CURRENT_DATE()
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
                WHERE
                    _DATA_DATE >= DATE_ADD(CURRENT_DATE(), INTERVAL -{days} DAY)
                    AND _DATA_DATE <> CURRENT_DATE()
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
                    RawDate AS Date,
                    Month,
                    EXTRACT(DAY FROM RawDate) AS Day, 
                    AVG(SAFE_CAST(REPLACE(SearchImpressionShare, '%', '') AS NUMERIC)) AS d0,
                FROM (
                    SELECT * FROM (
                        SELECT * FROM
                        UNNEST(
                            GENERATE_DATE_ARRAY(
                                DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                                CURRENT_DATE(),
                                INTERVAL 1 DAY
                            )
                        ) AS RawDate
                    ) _cal
                    LEFT JOIN (
                        SELECT * FROM
                        {dataset}.AccountNonClickStats_{table_suffix}
                        WHERE ExternalCustomerId = {external_customer_id}
                    ) b
                    ON _cal.RawDate = b._DATA_DATE
                )
                WHERE ExternalCustomerId = {external_customer_id}
                GROUP BY 1, 2, 3
            ),
            base2 AS (
                SELECT
                    Date,
                    Month,
                    d0,
                    LEAD(d0, 7) OVER (ORDER BY Date DESC) AS d7,
                    LEAD(d0, 1) OVER (PARTITION BY Day ORDER BY Month DESC) AS d_mom,
                FROM base
            ),
            base3 AS (
                SELECT
                    (
                        SELECT SUM(d0) FROM base2
                        WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                        AND Date <> CURRENT_DATE()
                    ) AS d7,
                    (
                        SELECT SUM(d7) FROM base2
                        WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                        AND Date <> CURRENT_DATE()
                    ) AS d14,
                    (
                        SELECT SUM(d0) FROM base2
                        WHERE Date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                        AND Date <> CURRENT_DATE()
                    ) AS dtm,
                    (
                        SELECT SUM(d_mom) FROM base2
                        WHERE Date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                        AND Date <> CURRENT_DATE()
                    ) AS dlm,
            )
            SELECT
                SAFE_DIVIDE(d7-d14,d14) AS dw,
                SAFE_DIVIDE(dtm-dlm, dlm) AS dmom,
            FROM base3
    """
    )


def metric_topsis() -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    RawDate AS Date,
                    Month,
                    EXTRACT(DAY FROM RawDate) AS Day, 
                    AVG(SAFE_CAST(REPLACE(SearchTopImpressionShare, '%', '') AS NUMERIC)) AS d0,
                FROM (
                    SELECT * FROM (
                        SELECT * FROM
                        UNNEST(
                            GENERATE_DATE_ARRAY(
                                DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                                CURRENT_DATE(),
                                INTERVAL 1 DAY
                            )
                        ) AS RawDate
                    ) _cal
                    LEFT JOIN (
                        SELECT * FROM
                        {dataset}.CampaignCrossDeviceStats_{table_suffix}
                        WHERE ExternalCustomerId = {external_customer_id}
                    ) b
                    ON _cal.RawDate = b._DATA_DATE
                )
                WHERE ExternalCustomerId = {external_customer_id}
                GROUP BY 1, 2, 3
            ),
            base2 AS (
                SELECT
                    Date,
                    Month,
                    d0,
                    LEAD(d0, 7) OVER (ORDER BY Date DESC) AS d7,
                    LEAD(d0, 1) OVER (PARTITION BY Day ORDER BY Month DESC) AS d_mom,
                FROM base
            ),
            base3 AS (
                SELECT
                    (
                        SELECT SUM(d0) FROM base2
                        WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                        AND Date <> CURRENT_DATE()
                    ) AS d7,
                    (
                        SELECT SUM(d7) FROM base2
                        WHERE Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                        AND Date <> CURRENT_DATE()
                    ) AS d14,
                    (
                        SELECT SUM(d0) FROM base2
                        WHERE Date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                        AND Date <> CURRENT_DATE()
                    ) AS dtm,
                    (
                        SELECT SUM(d_mom) FROM base2
                        WHERE Date >= DATE_TRUNC(CURRENT_DATE(), MONTH)
                        AND Date <> CURRENT_DATE()
                    ) AS dlm,
            )
            SELECT
                SAFE_DIVIDE(d7-d14,d14) AS dw,
                SAFE_DIVIDE(dtm-dlm, dlm) AS dmom,
            FROM base3
    """
    )


def ad_group_cpa() -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    ag.AdGroupName,
                    c.CampaignName,
                    SUM(ags.Cost / 1e6) AS Cost,
                    SUM(ags.Conversions) AS Conversions,
                FROM (
                    SELECT * FROM (
                        SELECT * FROM
                        UNNEST(
                            GENERATE_DATE_ARRAY(
                                DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                                CURRENT_DATE(),
                                INTERVAL 1 DAY
                            )
                        ) AS RawDate
                    ) _cal
                    LEFT JOIN (
                        SELECT * FROM
                        {dataset}.AdGroupStats_{table_suffix} ags
                        WHERE ExternalCustomerId = {external_customer_id}
                    ) b
                    ON _cal.RawDate = b._DATA_DATE
                ) ags
                INNER JOIN {dataset}.AdGroup_{table_suffix} ag
                    ON ags.AdGroupId = ag.AdGroupId
                    AND ags.CampaignId = ag.CampaignId
                INNER JOIN {dataset}.Campaign_{table_suffix} c
                    ON ags.CampaignId = c.CampaignId
                WHERE
                    ags.RawDate >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND ags.RawDate <> CURRENT_DATE()
                    AND ags.ExternalCustomerId = {external_customer_id}
                    AND ag._DATA_DATE = ag._LATEST_DATE
                    AND c._DATA_DATE = c._LATEST_DATE
                GROUP BY 1, 2
            ),
            base2 AS (
                SELECT
                    AdGroupName,
                    CampaignName,
                    Cost,
                    Conversions,
                    SAFE_DIVIDE(Cost, Conversions) AS cpa,
                    (SELECT SAFE_DIVIDE(SUM(Cost), SUM(Conversions)) FROM base) AS avg_cpa,
                FROM base
            )
            SELECT 
                ARRAY_AGG(AdGroupName || ' - ' || CampaignName) AS values,
                AVG(avg_cpa) AS avg,
            FROM base2 
            WHERE SAFE_DIVIDE(cpa - avg_cpa, avg_cpa) > 0.3
        """
    )


def keyword_cpa() -> Getter:
    return (
        lambda dataset, table_suffix, external_customer_id: f"""
            WITH base AS (
                SELECT
                    kw.Criteria ,
                    ag.AdGroupName,
                    c.CampaignName,
                    SUM(kws.Cost / 1e6) AS Cost,
                    SUM(kws.Conversions) AS Conversions,
                FROM (
                    SELECT * FROM (
                        SELECT * FROM
                        UNNEST(
                            GENERATE_DATE_ARRAY(
                                DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                                CURRENT_DATE(),
                                INTERVAL 1 DAY
                            )
                        ) AS RawDate
                    ) _cal
                    LEFT JOIN (
                        SELECT * FROM
                        {dataset}.KeywordStats_{table_suffix} kws
                        WHERE ExternalCustomerId = {external_customer_id}
                    ) b
                    ON _cal.RawDate = b._DATA_DATE
                ) kws
                INNER JOIN {dataset}.Keyword_{table_suffix} kw
                    ON kws.CriterionId = kw.CriterionId
                    AND kws.AdGroupId = kw.AdGroupId
                    AND kws.CampaignId = kw.CampaignId
                INNER JOIN {dataset}.AdGroup_{table_suffix} ag
                    ON kws.AdGroupId = ag.AdGroupId
                    AND kws.CampaignId = ag.CampaignId
                INNER JOIN {dataset}.Campaign_{table_suffix} c
                    ON kws.CampaignId = c.CampaignId
                WHERE
                    kws.RawDate >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND kws.RawDate <> CURRENT_DATE()
                    AND kws.ExternalCustomerId = {external_customer_id}
                    AND kw._DATA_DATE = kw._LATEST_DATE
                    AND ag._DATA_DATE = ag._LATEST_DATE
                    AND c._DATA_DATE = c._LATEST_DATE
                GROUP BY 1, 2, 3
            ),
            base2 AS (
                SELECT
                    Criteria,
                    AdGroupName,
                    CampaignName,
                    Cost,
                    Conversions,
                    SAFE_DIVIDE(Cost, Conversions) AS cpa,
                    (SELECT SAFE_DIVIDE(SUM(Cost), SUM(Conversions)) FROM base) AS avg_cpa
                FROM base
            )
            SELECT 
                ARRAY_AGG(Criteria || ' - ' || AdGroupName || ' - ' || CampaignName) AS values,
                AVG(avg_cpa) AS avg
            FROM base2 
            WHERE SAFE_DIVIDE(cpa - avg_cpa, avg_cpa) > 0.3
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
                FROM (
                    SELECT * FROM (
                        SELECT * FROM
                        UNNEST(
                            GENERATE_DATE_ARRAY(
                                DATE_ADD(CURRENT_DATE(), INTERVAL -90 DAY),
                                CURRENT_DATE(),
                                INTERVAL 1 DAY
                            )
                        ) AS RawDate
                    ) _cal
                    LEFT JOIN (
                        SELECT * FROM
                        {dataset}.AdGroupStats_{table_suffix} kws
                        WHERE ExternalCustomerId = {external_customer_id}
                    ) b
                    ON _cal.RawDate = b._DATA_DATE
                ) ags
                INNER JOIN {dataset}.AdGroup_{table_suffix} ag
                    ON ags.CampaignId = ag.CampaignId
                    AND ags.AdGroupId = ag.AdGroupId
                INNER JOIN {dataset}.Campaign_{table_suffix} c
                    ON ags.CampaignId = c.CampaignId
                WHERE
                    ags.ExternalCustomerId = {external_customer_id}
                    AND ag._DATA_DATE = ag._LATEST_DATE
                    AND c._DATA_DATE = c._LATEST_DATE

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
                WHERE
                    Date >= DATE_ADD(CURRENT_DATE(), INTERVAL -7 DAY)
                    AND Date <> CURRENT_DATE()
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
                        SAFE_DIVIDE((d0 - d7), d7) AS d7,
                        SAFE_DIVIDE((d0 - d30), d30) AS d30
                    )
                ) AS value
                FROM base4
            )
            SELECT * FROM base5
            WHERE ARRAY_LENGTH(value) > 0
    """
    )
