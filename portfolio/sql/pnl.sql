SELECT SUM("quantity") as owned, sum(total) as profit_and_loss, sum(value) as trade_volume_in_fiat, sum(fee) as spent_on_fees, asset
FROM "Transaction" group by asset, currency order by asset