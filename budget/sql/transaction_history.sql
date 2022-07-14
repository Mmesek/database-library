SELECT
    operation.timestamp, 
    sender.name as sender, 
    receiver.name as receiver, 
    operation.description,
    transaction.amount
FROM operation
    JOIN wallet as sender ON (
        sender.id = operation.sender_id
    ) 
    JOIN wallet as receiver ON (
        receiver.id = operation.recipent_id
    )
    JOIN transaction ON (
        operation.id = transaction.operation_id
)
WHERE transaction.wallet_id = 1
;