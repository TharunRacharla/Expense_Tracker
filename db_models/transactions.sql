CREATE TABLE transactions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,

    txn_date DATETIME NOT NULL,

    txn_type TEXT NOT NULL
        CHECK(txn_type IN (
            'income',
            'expense',
            'transfer'
        )),

    category TEXT,

    description TEXT,

    amount REAL NOT NULL,

    destination_account_id INTEGER,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(account_id)
        REFERENCES accounts(id),

    FOREIGN KEY(destination_account_id)
        REFERENCES accounts(id)
);