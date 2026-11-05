import re
import os

schema_path = os.path.join(os.path.dirname(__file__), "..", "schema", "smiota_consolidated_schema.sql")

with open(schema_path, "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

tables = re.findall(r"CREATE TABLE\s+[`\"]?([a-zA-Z0-9_]+)[`\"]?", sql, re.IGNORECASE)
print(f"Total tables found: {len(tables)}")
for i, t in enumerate(sorted(tables), 1):
    print(f"{i:2d}. {t}")
