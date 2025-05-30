import psycopg2
import requests

# GenAI Config
genai_api_base = "https://integrate.api.nvidia.com/v1"
genai_api_key = "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"

def genai_map_type(col_name, base_type):
    try:
        prompt = f"Map this to PostgreSQL datatype. Give only the type. No explanation.\nColumn: {col_name}\nDB2 Type: {base_type}"

        headers = {
            "Authorization": f"Bearer {genai_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta/llama3-8b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "top_p": 0.7,
            "max_tokens": 50
        }

        response = requests.post(f"{genai_api_base}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        suggestion = result["choices"][0]["message"]["content"].strip().upper()

        if any(word in suggestion.lower() for word in ["column", "type", "is"]):
            raise ValueError(f"Unexpected verbosity: {suggestion}")

        print(f"GenAI mapped: {col_name} -> {suggestion}")
        return suggestion
    except Exception as e:
        print(f"GenAI fallback for {col_name} due to: {e}")
        return base_type

def fetch_existing_data(cursor, limit=3):
    try:
        cursor.execute("SELECT * FROM testa LIMIT %s;", (limit,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        data_samples = [dict(zip(columns, row)) for row in rows]
        return data_samples
    except Exception as e:
        print(f"Error fetching existing data: {e}")
        return []

def generate_test_cases(procedure_name, existing_data):
    test_case_prompt = f"""
    Generate 5 SQL test cases for the PostgreSQL procedure '{procedure_name}'.
    This procedure inserts into a table 'testa' with these columns:
    {[col for col in existing_data[0].keys()]}

    Only return valid 'CALL {procedure_name}(...);' statements.
    Do not use empty strings for numeric fields. Use NULL if needed.
    Use realistic formats for phone numbers as numbers
    Use realistic but varied data based on this sample:
    {existing_data}
    """

    headers = {
        "Authorization": f"Bearer {genai_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta/llama3-8b-instruct",
        "messages": [{"role": "user", "content": test_case_prompt}],
        "temperature": 0.4,
        "top_p": 0.8,
        "max_tokens": 800
    }

    try:
        response = requests.post(f"{genai_api_base}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        test_cases = result["choices"][0]["message"]["content"].strip()

        print("Generated Test Cases:\n")
        print(test_cases)
        return test_cases
    except Exception as e:
        print(f"Error generating test cases: {e}")
        return None

def generate_validation_queries(table_name, sample_data):
    validation_prompt = f"""
    Given the table '{table_name}' and this sample data:
    {sample_data}

    Generate 3 SQL validation queries to:
    1. Verify that the inserted data exists correctly.
    2. Check for nulls in any of the fields.
    3. Count total rows in the table.

    Only return SQL queries. No explanation.
    """

    headers = {
        "Authorization": f"Bearer {genai_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta/llama3-8b-instruct",
        "messages": [{"role": "user", "content": validation_prompt}],
        "temperature": 0.3,
        "top_p": 0.8,
        "max_tokens": 300
    }

    try:
        response = requests.post(f"{genai_api_base}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        validation_sql = result["choices"][0]["message"]["content"].strip()
        print("\nGenerated Validation Queries:\n")
        print(validation_sql)
        return validation_sql
    except Exception as e:
        print(f"Error generating validation queries: {e}")
        return ""

def execute_test_case(cursor, test_case_sql):
    try:
        cursor.execute(test_case_sql)
        print(f"Executed test case:\n{test_case_sql}")
    except Exception as e:
        print(f"Error executing test case:\n{test_case_sql}\nError: {e}")

def run_validation(cursor, validation_sql):
    for line in validation_sql.strip().splitlines():
        if line.strip().lower().startswith("select"):
            try:
                cursor.execute(line.strip())
                results = cursor.fetchall()
                print(f"\nValidation Result for: {line.strip()}")
                for row in results:
                    print(row)
            except Exception as e:
                print(f"Error executing validation query:\n{line.strip()}\nError: {e}")

def migrate_procedure(pg_user, pg_password, pg_host, pg_port, pg_dbname, procedure_name):
    try:
        postgres_conn = psycopg2.connect(
            dbname=pg_dbname,
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port
        )
        print("PostgreSQL connection established.")

        cursor = postgres_conn.cursor()

        columns = [
            ("empno", "DECIMAL(8)"),
            ("empname", "CHAR(20)"),
            ("workdept", "CHAR(3)"),
            ("phoneno", "DECIMAL(10)"),
            ("job", "CHAR(8)"),
            ("sex", "CHAR(1)"),
            ("salary", "DECIMAL(9,2)"),
            ("bonus", "DECIMAL(9,2)"),
            ("balance", "DECIMAL(9,2)")
        ]

        pg_columns = [(name, genai_map_type(name, dtype)) for name, dtype in columns]

        table_cols_sql = ",\n    ".join([f"{name} {dtype}" for name, dtype in pg_columns])
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS testa (
            {table_cols_sql}
        );
        """

        proc_args = ",\n    ".join([f"{name} {dtype}" for name, dtype in pg_columns])
        insert_cols = ", ".join([col[0] for col in pg_columns])
        insert_vals = ", ".join([f"${i+1}" for i in range(len(pg_columns))])
        create_procedure_sql = f"""
        CREATE OR REPLACE PROCEDURE {procedure_name}(
            {proc_args}
        )
        LANGUAGE plpgsql
        AS $$ 
        BEGIN
            INSERT INTO testa ({insert_cols})
            VALUES ({insert_vals});
        END;
        $$;
        """

        drop_function_sql = f"DROP PROCEDURE IF EXISTS {procedure_name};"

        cursor.execute(create_table_sql)
        print("Table created.")
        cursor.execute(drop_function_sql)
        print("Existing procedure dropped.")
        cursor.execute(create_procedure_sql)
        print("New procedure created.")
        postgres_conn.commit()
        print("Migration committed successfully.")

        existing_data = fetch_existing_data(cursor)

        if not existing_data:
            print("No existing data found. Inserting a mock row for testing.")
            mock_insert = """
            INSERT INTO testa VALUES 
            (1001, 'Alice Smith', 'D01', 9876543210, 'CLERK', 'F', 50000.00, 3000.00, 1000.00);
            """
            cursor.execute(mock_insert)
            postgres_conn.commit()
            existing_data = fetch_existing_data(cursor)

        if existing_data:
            test_cases = generate_test_cases(procedure_name, existing_data)
            if test_cases:
                for line in test_cases.strip().splitlines():
                    if line.strip().lower().startswith("call"):
                        execute_test_case(cursor, line.strip())
                postgres_conn.commit()
 
        validation_sql = generate_validation_queries("testa", existing_data)
        if validation_sql:
            run_validation(cursor, validation_sql)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'postgres_conn' in locals():
            postgres_conn.close()
        print("PostgreSQL connection closed.")

pg_user = "postgres"
pg_password = "sheela"
pg_host = "localhost"
pg_port = "5432"
pg_dbname = "dcc"
procedure_name = "insert_employeez"

migrate_procedure(pg_user, pg_password, pg_host, pg_port, pg_dbname, procedure_name)
