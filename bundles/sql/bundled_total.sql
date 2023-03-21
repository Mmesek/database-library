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