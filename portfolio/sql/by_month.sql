WITH a AS (
  SELECT 
    SUM("total") AS balance, 
    EXTRACT(YEAR FROM "timestamp") AS year, EXTRACT(MONTH FROM "timestamp") AS month, 
    exchange
  FROM "Transaction"
  WHERE "type" != 'REWARD' /* Optional */
  GROUP BY EXTRACT(YEAR FROM "timestamp"), EXTRACT(MONTH FROM "timestamp"), exchange
),
b AS (
  SELECT 
    SUM("total") AS deposit, 
    EXTRACT(YEAR FROM "timestamp") AS year, EXTRACT(MONTH FROM "timestamp") as month,
    exchange
  FROM "Transaction"
  WHERE "type" IN ('DEPOSIT', 'EXTERNAL TRANSFER')
  GROUP BY EXTRACT(YEAR FROM "timestamp"), EXTRACT(MONTH FROM "timestamp"), exchange
)
SELECT a.balance, b.deposit, a.year, a.month, a.exchange
FROM a
INNER JOIN b ON a.year = b.year AND a.month = b.month AND a.exchange = b.exchange
order by year, month;