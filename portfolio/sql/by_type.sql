SELECT SUM("value") as volume, SUM("total") as balance, (SUM("value")-SUM("total")) as diff, type
FROM "Transaction"
group by "type"