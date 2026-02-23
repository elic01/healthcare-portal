import os
import psycopg2
from dotenv import load_dotenv
import time

load_dotenv()

def run_sql_file(cursor, file_path):
    print(f"Executing {file_path}...")
    with open(file_path, 'r') as f:
        sql = f.read()
        cursor.execute(sql)

def setup_db():
    dbname = os.getenv("LOCAL_DB_NAME", "healthcare_portal")
    user = os.getenv("LOCAL_DB_USER", "postgres")
    password = os.getenv("LOCAL_DB_PASSWORD", "postgres")
    host = os.getenv("LOCAL_DB_HOST", "localhost")
    port = os.getenv("LOCAL_DB_PORT", "5432")

    # Connect to default postgres to create the DB if it doesn't exist
    try:
        conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
            cursor.execute(f"CREATE DATABASE {dbname}")
        conn.close()
        print(f"Database '{dbname}' created successfully.")
    except Exception as e:
        print(f"Error creating database: {e}")
        return

    # Connect to the new DB and run schema
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        with conn.cursor() as cursor:
            run_sql_file(cursor, 'sql/supabase_schema.sql')
            run_sql_file(cursor, 'sql/add_missing_columns.sql')
            run_sql_file(cursor, 'sql/create_admin.sql')
            run_sql_file(cursor, 'sql/seed_data.sql')
        conn.commit()
        conn.close()
        print("Schema applied successfully!")
    except Exception as e:
        print(f"Error applying schema: {e}")

if __name__ == "__main__":
    setup_db()
