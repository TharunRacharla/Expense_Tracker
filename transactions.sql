CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
    txn_date DATE,
    txn_type ENUM(
        'income',
        'expense',
        'transfer'
    ),
    category VARCHAR(100),
    amount DECIMAL(12,2),
    description VARCHAR(255)
);