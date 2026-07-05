WITH asset_leg AS (
    SELECT
        id,
        exchange,
        timestamp,
        type,
        external_id,
        quantity,
        asset,
        price,
        currency,
        rate as "NBP-1",
        fee,
        value,
        total,
        note,
        false as reversed
    FROM
        "Transaction"
),
currency_leg AS (
    SELECT
        t.id,
        t.exchange,
        t.timestamp,
        CASE
            WHEN LOWER(t.type) = 'buy' THEN 'SELL'
            ELSE 'BUY'
        END as type,
        t.external_id,
        CASE
            WHEN LOWER(t.type) = 'buy' THEN - t.value
            ELSE t.total
        END as quantity,
        t.currency as asset,
        CASE
            WHEN t.price != 0 THEN 1.0 / t.price
            ELSE 0
        END as price,
        t.asset as currency,
        t.rate as "NBP-1",
        0 as fee,
        CASE
            WHEN LOWER(t.type) = 'buy' THEN - t.quantity
            ELSE t.quantity
        END as value,
        CASE
            WHEN LOWER(t.type) = 'buy' THEN - t.quantity
            ELSE t.quantity
        END as total,
        t.note,
        true as reversed
    FROM
        "Transaction" t
),
combined as (
    SELECT
        *
    FROM
        asset_leg
    UNION
    ALL
    SELECT
        *
    FROM
        currency_leg
),
positions as (
    SELECT
        ROW_NUMBER() OVER (
            PARTITION BY asset
            ORDER BY
                type,
                timestamp,
                id
        ) AS position,
        *
    FROM
        combined
    WHERE
        timestamp >= '2026-05-01'
        AND timestamp < '2026-06-01'
        AND type != 'DEPOSIT'
        AND type != 'WITHDRAW'
)
SELECT
    COALESCE(w2.position, 0) AS linked_position,
    w1.*
FROM
    positions w1
    LEFT JOIN positions w2 ON w1.id = w2.id
    AND w1.reversed != w2.reversed
ORDER BY
    timestamp,
    id ASC