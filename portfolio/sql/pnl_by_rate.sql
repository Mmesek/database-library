SELECT sum(quantity) as eur, sum(quantity * rate) as pln, avg(rate) as avg_rate, avg(quantity) as avg_quantity
FROM "Transaction" 
WHERE asset='EUR' AND type IN ('BUY', 'SELL');

SELECT sum(fee), sum(fee * rate)
FROM "Transaction"
WHERE asset != 'EUR';
