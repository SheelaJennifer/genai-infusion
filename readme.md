# 🚀 GenAI-Powered DB2 ➜ PostgreSQL Migration Toolkit

> **Infusing Generative AI into legacy data migration for faster, smarter, and scalable modernization**

---

##  Overview

This project automates the traditionally manual and error-prone process of **migrating DB2 LUW stored procedures and schemas** into **PostgreSQL**, using **Generative AI (OpenAI GPT-4.5)**.  
It drastically reduces development time, improves accuracy, and allows scalable, reusable migrations.

---

##  Key Features

-  **Stored Procedure Conversion** – Translates DB2 procedures into PostgreSQL using GPT
-  **Built-in Validation & Test Generation** – Auto-generates test cases for converted SPs
-  **DDL + Data Load Automation** – Builds schema and populates tables from flat files
-  **Reusable & Modular Scripts** – Designed for scale and easy integration
-  **Powered by GenAI** – Uses LLM prompts for conversion, DDL generation, and testing

---

##  Project Structure

```bash
genai
│
├── script1_sp_conversion_validation.py   # Main script for SP conversion + validation
├── script2_ddl_data_load.py              # Script for generating DDL & loading data
├── examples/                             # Sample input/output DB2 + PG scripts
├── requirements.txt                      # Python dependencies
├── .env                                  # OpenAI API key and DB credentials
└── README.md                             
```

---

##  How It Works

1. **Stored Procedure Conversion**  
   - Input: DB2 LUW SP text  
   - Output: PostgreSQL-compatible SP with test cases  
   - Method: GPT prompt + validation logic

2. **DDL & Data Load**  
   - Input: CSV file + column metadata  
   - Output: PG DDL and insert/load script  
   - Method: GPT + dynamic Python mapping

---

## ⚙️ Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/your-username/genai-db2pg-migration.git
cd genai-db2pg-migration
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API & DB credentials**

Update `.env` with:
```bash
OPENAI_API_KEY=your_openai_key
DB_HOST=your_pg_host
DB_NAME=your_pg_db
DB_USER=your_pg_user
DB_PASS=your_pg_pass
```

4. **Run the scripts**

```bash
# Convert DB2 stored procedures
python script1_sp_conversion_validation.py

# Generate schema and load data
python script2_ddl_data_load.py
```

---

##  Tech Stack

-  OpenAI GPT-4.5 – Code generation, DDL creation, testing logic
-  Python – Main driver for logic, file I/O, DB ops
-  PostgreSQL – Target modern database
-  psycopg2 – PostgreSQL connector
-  dotenv – Credential management

---

## 📊 Sample Results

```bash
Activity             | Traditional Time | GenAI Time | Accuracy
---------------------|------------------|------------|---------
SP Conversion        | 1–2 hrs/SP       | <10 mins   | ~90%
DDL + Data Load      | 30–60 mins/table | ~5 mins    | ~95%
Validation/Test Case | Manual scripting | Auto-gen   | Consistent
```

---

## 💡 Why This Matters

This toolkit demonstrates how **Generative AI can accelerate digital transformation**, reduce technical debt, and enable modernization without exhaustive manual labor.

---

##  Contributing

Pull requests, ideas, and issues are welcome!  
If you’ve tried a similar GenAI use case or want to extend this for other databases, feel free to contribute.

---


## 📌 Note

This project is designed for **educational and portfolio purposes**, simulating real-world DB2 ➜ PostgreSQL modernization use cases while showcasing GenAI's transformative power.
