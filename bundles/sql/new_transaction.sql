CREATE OR REPLACE FUNCTION "new_transaction"() RETURNS 
trigger 
LANGUAGE plpgsql AS 
$$
BEGIN
	INSERT INTO
	    "Transaction" ("Transaction".id)
	VALUES (OLD.id);
	RETURN OLD;
END;
$$; 

CREATE TRIGGER "tg_new_transaction" INSTEAD OF DELETE ON "public"."BundledGames" FOR EACH ROW EXECUTE FUNCTION new_transaction();
