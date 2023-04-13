PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
email TEXT NOT NULL,
password TEXT NOT NULL,
session_token TEXT,
verification_token TEXT,
verified INTEGER DEFAULT 0 CHECK(verified IN (0, 1)));
DELETE FROM sqlite_sequence;
COMMIT;
