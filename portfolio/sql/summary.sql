SELECT 
  asset, 
  sum(quantity), 
  AVG(CASE WHEN quantity > 0 AND price != 0 THEN price ELSE NULL END) AS avg_buy_price,
  AVG(CASE WHEN quantity < 0 AND price != 0 THEN price ELSE NULL END) AS avg_sell_price, 
  min(CASE WHEN price != 0 THEN price ELSE NULL END), 
  max(CASE WHEN price != 0 THEN price ELSE NULL END), 
  currency
FROM "Transaction"
GROUP BY "asset", currency