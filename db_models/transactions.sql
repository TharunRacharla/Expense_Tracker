CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    txn_date DATETIME NOT NULL,
    txn_type ENUM('income', 'expense', 'transfer') NOT NULL,
    category VARCHAR(100),
    description VARCHAR(255),
    amount DECIMAL(12 , 2 ) NOT NULL,
    destination_account_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id)
        REFERENCES accounts (id),
    FOREIGN KEY (destination_account_id)
        REFERENCES accounts (id)
);