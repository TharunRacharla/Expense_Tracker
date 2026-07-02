CREATE TABLE holdings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    asset_name VARCHAR(150) NOT NULL,
    asset_type ENUM('mutual_fund', 'stock', 'etf', 'gold', 'fd', 'bond', 'other') NOT NULL,
    amount_invested DECIMAL(12 , 2 ) NOT NULL,
    last_updated_value DECIMAL(12 , 2 ) NOT NULL,
    investment_type ENUM('one_time', 'sip') DEFAULT 'one_time',
    sip_amount DECIMAL(12 , 2 ) DEFAULT NULL,
    sip_frequency ENUM('weekly', 'monthly', 'quarterly', 'yearly') DEFAULT NULL,
    start_date DATE DEFAULT NULL,
    notes VARCHAR(255),
    updated_on DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id)
        REFERENCES accounts (id)
);