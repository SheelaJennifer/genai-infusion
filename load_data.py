# load_data.py

import pandas as pd
import psycopg2
import requests
import io

# GenAI config
genai_api_base = "https://integrate.api.nvidia.com/v1"
genai_api_key = "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"

def call_genai(prompt, max_tokens=500):
    headers = {
        "Authorization": f"Bearer {genai_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta/llama3-8b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "top_p": 0.8,
        "max_tokens": max_tokens
    }

    response = requests.post(f"{genai_api_base}/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

def generate_ddl_from_csv(csv_path, table_name):
    df = pd.read_csv(csv_path)
    sample_data = df.head(5).to_dict(orient='records')

    prompt = f"""
Given the following CSV column names and sample rows, generate a PostgreSQL CREATE TABLE statement for table '{table_name}'.
Infer appropriate data types. Only return the SQL, no explanation.

Columns: {list(df.columns)}
Sample Rows:
{sample_data}
"""
    ddl = call_genai(prompt)
    print("\n--- Generated DDL ---\n")
    print(ddl)
    return ddl, df

def execute_ddl(ddl_sql, pg_user, pg_password, pg_host, pg_port, pg_dbname):
    try:
        conn = psycopg2.connect(
            dbname=pg_dbname,
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port
        )
        cursor = conn.cursor()
        cursor.execute(ddl_sql)
        conn.commit()
        print("\nDDL executed successfully.")
    except Exception as e:
        print(f"Error executing DDL: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("PostgreSQL connection closed.")

def load_csv_with_copy(df, table_name, pg_user, pg_password, pg_host, pg_port, pg_dbname):
    try:
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        conn = psycopg2.connect(
            dbname=pg_dbname,
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port
        )
        cursor = conn.cursor()
        cursor.copy_from(buffer, table_name, sep=",", null="")
        conn.commit()
        print(f"\nCSV data successfully loaded into table '{table_name}' using copy_from.")
    except Exception as e:
        print(f"Error loading data with copy_from: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("PostgreSQL connection closed.")

# This is the callable function used by the DAG
def load_to_postgres():
    csv_path = r"/home/sheela/airflow/data/cleaned_orders.csv"
    table_name = "orderinfo_bq"
    pg_user = "postgres"
    pg_password = "sheela"
    pg_host = "localhost"
    pg_port = "5432"
    pg_dbname = "webtrace"

    ddl, df = generate_ddl_from_csv(csv_path, table_name)
    execute_ddl(ddl, pg_user, pg_password, pg_host, pg_port, pg_dbname)
    load_csv_with_copy(df, table_name, pg_user, pg_password, pg_host, pg_port, pg_dbname)
