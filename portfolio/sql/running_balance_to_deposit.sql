WITH a AS (
  SELECT SUM("total") AS balance 
  FROM "Transaction"
  WHERE "type" != 'REWARD' /* Optional */
),
b AS (
  SELECT SUM("total") AS deposit
  FROM "Transaction"
  WHERE "type" IN ('DEPOSIT', 'EXTERNAL TRANSFER')
)
SELECT a.balance, b.deposit
FROM a
CROSS JOIN b;