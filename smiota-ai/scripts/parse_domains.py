"""Script to parse the consolidated schema and separate tables into Core vs RAG/Enterprise domains."""
import re
import os

schema_path = os.path.join(os.path.dirname(__file__), "..", "schema", "smiota_consolidated_schema.sql")

with open(schema_path, "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

# Split by CREATE TABLE
table_blocks = re.findall(r"CREATE TABLE\s+[`\"]?([a-zA-Z0-9_]+)[`\"]?\s*\((.*?)\)\s*ENGINE", sql, re.DOTALL | re.IGNORECASE)

print(f"Total tables extracted: {len(table_blocks)}")

table_names = [t[0].lower() for t in table_blocks]

# Define Core domains vs RAG domains
core_keywords = ["package", "locker", "building", "location", "courier", "recipient", "user", "carrier"]

core_tables = []
rag_tables = []

for name in sorted(table_names):
    if any(k in name for k in ["package", "locker", "building", "location", "courier", "recipient"]) or name in ["user", "customer", "account"]:
        core_tables.append(name)
    else:
        rag_tables.append(name)

print("\n=== CORE CUSTOMER & LOCKER DOMAIN TABLES ===")
for t in core_tables:
    print(f"  - {t}")

print("\n=== RAG / ENTERPRISE TELEMETRY & CONFIG TABLES ===")
for t in rag_tables:
    print(f"  - {t}")
