SELECT 
    sender.name as wallet, 
    sum(transaction.amount) as balance, 
    sender.currency
FROM transaction 
    JOIN wallet as sender ON (
        sender.id = transaction.wallet_id
    ) 
    JOIN wallet as receiver ON (
        receiver.id = transaction.wallet_id
    )
GROUP BY sender.name, receiver.name, sender.currency
ORDER BY balance
;