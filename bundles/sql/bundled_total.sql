CREATE VIEW "BundledTotal" AS 
  SELECT 
    "Bundle".date,
    "Bundle".name AS bundle,
    sum(COALESCE("Offer".price, 0.0)) AS offer,
    sum(COALESCE("Price".price, 0.0)) AS price
  FROM ((((
    "Key"
    JOIN "Bundle" ON "Key".bundle_id = "Bundle".id)
    JOIN "Game" ON "Game".id = "Key".game_id)
    LEFT JOIN "Offer" ON "Key".id = "Offer".key_id)
    LEFT JOIN "Price" ON "Key".game_id = "Price".game_id)
  WHERE ("Key".used_date IS NULL)
  GROUP BY "Bundle".id;

  SELECT 
    extract(year FROM "Bundle".date) AS year, 
    "Bundle".name,
    sum(COALESCE("Transaction".price, 0.0)) - "Bundle".price AS profit,
    count(CASE WHEN "Key".used_date IS NULL THEN 1 ELSE NULL END) AS remaining
  FROM "Key" 
    LEFT JOIN "Transaction" ON "Transaction".key_id = "Key".id 
    JOIN "Bundle" ON "Bundle".id = "Key".bundle_id 
      AND "Bundle".id != 0 
      AND COALESCE("Bundle".currency, 'PLN') = COALESCE("Transaction".currency, 'PLN')
  GROUP BY "Bundle".id
  ORDER BY 
    remaining DESC, 
    year DESC,
    profit DESC
