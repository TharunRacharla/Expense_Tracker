CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    account_type ENUM(
        'savings',
        'current',
        'credit_card',
        'cash',
        'wallet'
        'dmat'
    ) NOT NULL,

    opening_balance DECIMAL(12,2) NOT NULL DEFAULT 0,
    current_balance DECIMAL(12,2) NOT NULL DEFAULT 0,

    credit_limit DECIMAL(12,2),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);