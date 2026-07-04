CREATE TABLE holdings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    account_id INTEGER NOT NULL,

    asset_name TEXT NOT NULL,

    asset_type TEXT NOT NULL
        CHECK(asset_type IN (
            'mutual_fund',
            'stock',
            'etf',
            'gold',
            'fd',
            'bond',
            'other'
        )),

    amount_invested REAL NOT NULL,

    last_updated_value REAL NOT NULL,

    investment_type TEXT DEFAULT 'one_time'
        CHECK(investment_type IN (
            'one_time',
            'sip'
        )),

    sip_amount REAL,

    sip_frequency TEXT
        CHECK(sip_frequency IN (
            'weekly',
            'monthly',
            'quarterly',
            'yearly'
        )),

    start_date DATE,

    notes TEXT,

    updated_on DATE,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(account_id)
        REFERENCES accounts(id)
);