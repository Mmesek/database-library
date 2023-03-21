CREATE VIEW "BundledGames" AS SELECT "Key".id,
    "Bundle".date,
    "Bundle".name AS bundle,
    "Game".name AS game,
    COALESCE("Offer".price, 0.0) AS offer,
    COALESCE("Price".price, 0.0) AS price,
    COALESCE(("Offer".price - "Price".price), 0.0) AS difference,
    "Key".expire_date
   FROM (((("Key"
     JOIN "Bundle" ON (("Key".bundle_id = "Bundle".id)))
     JOIN "Game" ON (("Game".id = "Key".game_id)))
     LEFT JOIN "Offer" ON (("Key".id = "Offer".key_id)))
     LEFT JOIN "Price" ON (("Key".game_id = "Price".game_id)))
  WHERE ("Key".used_date IS NULL);