create table accounts (
id int auto_increment primary key,
name varchar(100) not null,
account_type enum('savings', 'current', 'credit_card', 'cash', 'wallet') not null,
opening_balance decimal(12, 2) default 0,
current_balance decimal(12, 2) default 0,
created_at timestamp default current_timestamp
);