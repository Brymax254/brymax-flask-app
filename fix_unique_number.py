from sqlalchemy import create_engine, text

# Replace with your actual PostgreSQL connection details
DB_URL = "postgresql://brymax_db_0rar_user:UJAUb5GwFatfUxd5CvxCCltSNEN5asAf@dpg-cvjh7a24d50c73eep780-a.oregon-postgres.render.com/brymax_db_0rar"

# Create a database engine
engine = create_engine(DB_URL)

def check_and_fix_column():
    with engine.connect() as conn:
        # Step 1: Find records that are too long
        result = conn.execute(text("SELECT unique_number FROM farmer WHERE LENGTH(unique_number) > 10"))
        long_values = result.fetchall()

        if long_values:
            print(f"⚠️ Found {len(long_values)} records with values longer than 10 characters.")

            # Step 2: Truncate values (Optional, only if needed)
            conn.execute(text("UPDATE farmer SET unique_number = LEFT(unique_number, 10) WHERE LENGTH(unique_number) > 10"))
            conn.commit()
            print("✅ Truncated long values to fit within 10 characters.")

        # Step 3: Increase column size (Recommended)
        conn.execute(text("ALTER TABLE farmer ALTER COLUMN unique_number TYPE VARCHAR(20)"))
        conn.commit()
        print("✅ Increased `unique_number` column size to 20 characters.")

if __name__ == "__main__":
    check_and_fix_column()
