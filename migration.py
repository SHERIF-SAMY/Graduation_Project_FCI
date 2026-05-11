import sys
import sqlalchemy as sa
from sql.db import get_engine

try:
    engine = get_engine()
except ValueError as e:
    print(f"Error getting engine: {e}")
    sys.exit(1)

with engine.connect() as conn:
    print("Creating UserInteractions table...")
    conn.execute(sa.text("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='UserInteractions' AND xtype='U')
        BEGIN
            CREATE TABLE UserInteractions (
                Id                INT PRIMARY KEY IDENTITY,
                UserId            NVARCHAR(100) NULL,
                SessionId         NVARCHAR(100) NULL,
                ProductId         INT NULL,
                ActionType        NVARCHAR(50)  NOT NULL,
                SearchQuery       NVARCHAR(500) NULL,
                Category          NVARCHAR(100) NULL,
                Brand             NVARCHAR(100) NULL,
                LocationArea      NVARCHAR(100) NULL,
                PriceRange        FLOAT NULL,
                PreferredLanguage NVARCHAR(10)  NULL,
                CreatedAt         DATETIME DEFAULT GETDATE()
            );
            CREATE INDEX IX_UI_User    ON UserInteractions(UserId,    CreatedAt DESC);
            CREATE INDEX IX_UI_Session ON UserInteractions(SessionId, CreatedAt DESC);
            print('UserInteractions created.');
        END
        ELSE
        BEGIN
            print('UserInteractions already exists.');
        END
    """))

    print("Creating ProductStats table...")
    conn.execute(sa.text("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ProductStats' AND xtype='U')
        BEGIN
            CREATE TABLE ProductStats (
                ProductId         INT PRIMARY KEY,
                TotalViews        INT DEFAULT 0,
                TotalClicks       INT DEFAULT 0,
                TotalFavorites    INT DEFAULT 0,
                TotalRentRequests INT DEFAULT 0,
                LastUpdated       DATETIME DEFAULT GETDATE()
            );
            print('ProductStats created.');
        END
        ELSE
        BEGIN
            print('ProductStats already exists.');
        END
    """))
    conn.commit()

print("Migration completed.")
