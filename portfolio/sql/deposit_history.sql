SELECT "total" AS deposit, exchange, asset, timestamp
  FROM "Transaction"
  WHERE "type" IN ('DEPOSIT', 'EXTERNAL TRANSFER')