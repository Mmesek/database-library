SELECT 
    transaction.timestamp, 
    sender.name as sender, 
    receiver.name as receiver, 
    transaction.amount, 
    transaction.currency, 
    transaction.description
FROM transaction 
    JOIN wallet as sender ON (
        sender.id = transaction.sender_id
    ) 
    JOIN wallet as receiver ON (
        receiver.id = transaction.recipent_id
    )
;

SELECT 
    sender.name as sender, 
    receiver.name as receiver, 
    sum(transaction.amount), 
    transaction.currency
FROM transaction 
    JOIN wallet as sender ON (
        sender.id = transaction.sender_id
    ) 
    JOIN wallet as receiver ON (
        receiver.id = transaction.recipent_id
    )
WHERE
    transaction.sender_id = sender.id
    AND transaction.recipent_id = receiver.id
GROUP BY sender.name, receiver.name, transaction.currency
;

SELECT Receiver, Amount, timestamp, Balance, currency
FROM (
  SELECT recipent_id as Receiver, transaction.amount, timestamp, currency,
    SUM(transaction.amount) OVER(
      ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING 
  ) AS Balance
  FROM transaction
  GROUP BY Receiver, transaction.currency
) transaction
ORDER BY id
;

SELECT COALESCE(SUM(incoming.amount), 0.0) - COALESCE(SUM(outgoing.amount), 0.0) as balance, incoming.currency 
FROM transaction
JOIN transaction as incoming ON ((incoming.timestamp <= transaction.timestamp))
JOIN transaction as outgoing ON ((outgoing.timestamp <= transaction.timestamp))
GROUP BY incoming.currency

SELECT Receiver, timestamp, transaction.amount, Balance, currency
FROM (
  SELECT wallet.name as Receiver, timestamp, currency, transaction.amount,
    SUM(transaction.amount) OVER(
      ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND 0 PRECEDING 
  ) AS Balance
  FROM transaction JOIN wallet ON (transaction.wallet_id = wallet.id) JOIN operation ON (transaction.operation_id = operation.id)
) transaction
ORDER BY timestamp
;