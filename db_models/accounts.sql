CREATE TABLE IF NOT EXISTS accounts (
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
    starting_balance_update_time DATETIME NOT NULL,
    current_balance REAL NOT NULL DEFAULT 0,

    credit_limit REAL
);