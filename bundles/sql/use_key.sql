CREATE OR REPLACE FUNCTION "use_key"() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  UPDATE "Key"
  SET used_date = now()
  WHERE "Key".id = OLD.id;
  RETURN OLD;
END;
$$;

CREATE TRIGGER "tg_use_key" INSTEAD OF DELETE ON "public"."BundledGames" FOR EACH ROW EXECUTE FUNCTION use_key();;
