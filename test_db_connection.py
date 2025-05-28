import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://brymax_zra0_user:nD2AY6N2igHVYTEMYxQZszKuSDYyvCi6@dpg-d0rg54buibrs73d7881g-a.oregon-postgres.render.com/brymax_zra0?sslmode=require"

# Create the SQLAlchemy engine with pre-ping to avoid stale connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

try:
    with engine.connect() as conn:
        # Use `text()` to properly handle raw SQL
        result = conn.execute(text("SELECT 1"))
        print("Database connection successful:", result.scalar())
except Exception as e:
    print("Error connecting to database:", e)
