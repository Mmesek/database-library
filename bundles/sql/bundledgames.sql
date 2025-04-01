CREATE OR REPLACE VIEW "BundledGames" AS
SELECT "Key".id,
	"Bundle".date,
	"Bundle".name AS bundle,
	"Game".name AS game,
	COALESCE("Offer".price, 0.0) AS offer,
	COALESCE("Price".price, 0.0) AS price,
	COALESCE(("Offer".price - "Price".price), 0.0) AS difference
FROM (
		(
			(
				(
					"Key"
					JOIN "Bundle" ON (("Key".bundle_id = "bundle".id))
				)
				JOIN "Game" ON (("Game".id = "Key".game_id))
			)
			LEFT JOIN "Offer" ON (("Key".id = "Offer".key_id))
		)
		LEFT JOIN "Price" ON (("Key".game_id = "Price".game_id))
	)
WHERE ("Key".used_date IS NULL);

CREATE OR REPLACE FUNCTION "use_key"() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
UPDATE "Key"
SET
	used_date = now()
WHERE "Key".id = OLD.id;
RETURN OLD;
END;
$$;

CREATE OR REPLACE TRIGGER tg_use_key INSTEAD OF DELETE ON "BundledGames" FOR EACH ROW EXECUTE FUNCTION use_key ();
CREATE EXTENSION pg_trgm;
CREATE INDEX ON game USING gin(name gin_trgm_ops);
SELECT "Key".id,
	"Bundle".date,
	"Bundle".name AS
	OR REPLACE TRIGGER tg_use_key INSTEAD OF DELETE ON "BundledGames" FOR EACH ROW EXECUTE FUNCTION use_key ();

CREATE EXTENSION pg_trgm;
CREATE INDEX ON game USING gin(name gin_trgm_ops);
SELECT "Key".id,
	"Bundle".date,
	"Bundle".name AS bundle,
	"Game".name AS game,
	"Offer".price AS offer,
	COALESCE("Price".price, 0.0) AS price
FROM(
		(
			(
				(
					"Key"
					JOIN "Bundle" ON(("Key".bundle_id = "Bundle".id))
				)
				JOIN game ON(("Game".id = "Key".game_id))
			)
			LEFT JOIN offer ON(("Key".id = "Offer".key_id))
		)
		RIGHT JOIN price ON(("Key".game_id = "Price".game_id))
	)
WHERE(
		("Key".used_date IS NULL)
		AND("Offer".price IS NULL)
	);



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

DROP TABLE IF EXISTS "BundledTotal";
CREATE VIEW "BundledTotal" AS SELECT "Bundle".date,
    "Bundle".name AS bundle,
    sum(COALESCE("Offer".price, 0.0)) AS offer,
    sum(COALESCE("Price".price, 0.0)) AS price
   FROM (((("Key"
     JOIN "Bundle" ON (("Key".bundle_id = "Bundle".id)))
     JOIN "Game" ON (("Game".id = "Key".game_id)))
     LEFT JOIN "Offer" ON (("Key".id = "Offer".key_id)))
     LEFT JOIN "Price" ON (("Key".game_id = "Price".game_id)))
  WHERE ("Key".used_date IS NULL)
  GROUP BY "Bundle".id;

DROP TABLE IF EXISTS "NotListed";
CREATE VIEW "NotListed" AS SELECT "Key".id,
    "Bundle".date,
    "Bundle".name AS bundle,
    "Game".name AS game,
    "Offer".price AS offer,
    COALESCE("Price".price, 0.0) AS price
   FROM (((("Key"
     JOIN "Bundle" ON (("Key".bundle_id = "Bundle".id)))
     JOIN "Game" ON (("Game".id = "Key".game_id)))
     LEFT JOIN "Offer" ON (("Key".id = "Offer".key_id)))
     RIGHT JOIN "Price" ON (("Key".game_id = "Price".game_id)))
  WHERE (("Key".used_date IS NULL) AND ("Offer".price IS NULL));
