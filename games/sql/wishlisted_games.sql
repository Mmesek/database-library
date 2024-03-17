SELECT "Game".name AS game,
    "Bundle".name AS bundle,
    COALESCE("BundledTotal".profit, (0)::numeric) AS "Bundle Cost",
    "Price".price,
    "Wishlist".hltb_story AS "Story",
    "Wishlist".hltb_total AS "Completion"
FROM "Wishlist"
    JOIN "Game" ON "Game".id = "Wishlist".game_id
    JOIN "Key" ON "Key".game_id = "Wishlist".game_id AND "Key".used_date IS NULL
    JOIN "Bundle" ON "Key".bundle_id = "Bundle".id
    LEFT JOIN "BundledTotal" ON ("BundledTotal".name)::text = ("Bundle".name)::text
    LEFT JOIN "Price" ON "Price".game_id = "Wishlist".game_id
ORDER BY COALESCE("BundledTotal".profit, (0)::numeric) DESC;