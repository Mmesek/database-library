SELECT 
  asset, 
  sum(quantity), 
  AVG(CASE WHEN quantity > 0 THEN price ELSE NULL END) AS avg_buy_price,
  AVG(CASE WHEN quantity < 0 THEN price ELSE NULL END) AS avg_sell_price, 
  min(price), 
  max(price), 
  currency
FROM "Transaction"
GROUP BY "asset", currency