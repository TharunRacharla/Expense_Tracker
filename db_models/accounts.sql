CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    account_type TEXT NOT NULL
        CHECK(account_type IN (
            'savings',
            'current',
            'credit_card',
            'cash',
            'wallet',
            'dmat'
        )),

    opening_balance REAL NOT NULL DEFAULT 0,

    current_balance REAL NOT NULL DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    credit_limit REAL
);