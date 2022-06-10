CREATE OR REPLACE VIEW "BundledGames" AS
SELECT key.id,
	bundle.date,
	bundle.name AS bundle,
	game.name AS game,
	COALESCE(offer.price, 0.0) AS offer,
	COALESCE(price.price, 0.0) AS price,
	COALESCE((offer.price - price.price), 0.0) AS difference
FROM (
		(
			(
				(
					key
					JOIN bundle ON ((key.bundle_id = bundle.id))
				)
				JOIN game ON ((game.id = key.game_id))
			)
			LEFT JOIN offer ON ((key.id = offer.key_id))
		)
		LEFT JOIN price ON ((key.game_id = price.game_id))
	)
WHERE (key.used = false);

CREATE OR REPLACE FUNCTION "use_key"() RETURNS trigger LANGUAGE plpgsql AS $ $ BEGIN
UPDATE key
SET used = True,
	used_date = now()
WHERE key.id = OLD.id;
RETURN OLD;
END;
$$;

CREATE OR REPLACE TRIGGER tg_use_key INSTEAD OF DELETE ON "BundledGames" FOR EACH ROW EXECUTE FUNCTION use_key ();
CREATE EXTENSION pg_trgm;
CREATE INDEX ON game USING gin(name gin_trgm_ops);
SELECT key.id,
	bundle.date,
	bundle.name AS
	OR REPLACE TRIGGER tg_use_key INSTEAD OF DELETE ON "BundledGames" FOR EACH ROW EXECUTE FUNCTION use_key ();

CREATE EXTENSION pg_trgm;
CREATE INDEX ON game USING gin(name gin_trgm_ops);
SELECT key.id,
	bundle.date,
	bundle.name AS bundle,
	game.name AS game,
	offer.price AS offer,
	COALESCE(price.price, 0.0) AS price
FROM(
		(
			(
				(
					key
					JOIN bundle ON((key.bundle_id = bundle.id))
				)
				JOIN game ON((game.id = key.game_id))
			)
			LEFT JOIN offer ON((key.id = offer.key_id))
		)
		RIGHT JOIN price ON((key.game_id = price.game_id))
	)
WHERE(
		(key.used = false)
		AND(offer.price IS NULL)
	);
