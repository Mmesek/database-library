SELECT SUM("quantity"), asset, MIN("price"), MAX("price"), COUNT("asset")
FROM "Transaction"

group by "asset"