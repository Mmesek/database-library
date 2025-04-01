WITH a AS (
  SELECT SUM("total") AS balance, exchange, asset
  FROM "Transaction"
  WHERE "type" != 'REWARD' /* Optional */
  GROUP BY exchange, asset
),
b AS (
  SELECT SUM("total") AS deposit, exchange, asset
  FROM "Transaction"
  WHERE "type" IN ('DEPOSIT', 'EXTERNAL TRANSFER')
  GROUP BY exchange, asset
)
SELECT a.balance, b.deposit, a.exchange, b.asset
FROM a
INNER JOIN b ON a.exchange = b.exchange AND a.asset = b.asset;