import re
import os

schema_path = os.path.join(os.path.dirname(__file__), "..", "schema", "smiota_consolidated_schema.sql")

with open(schema_path, "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

target_tables = [
    "package", "locker"
]

for t in target_tables:
    m = re.search(r"CREATE TABLE\s+[`\"]?" + t + r"[`\"]?\s*\((.*?)\)\s*ENGINE", sql, re.DOTALL | re.IGNORECASE)
    if m:
        lines = m.group(1).split("\n")
        cols = [l.strip().rstrip(",") for l in lines if l.strip() and not l.strip().upper().startswith(("PRIMARY", "UNIQUE", "KEY", "CONSTRAINT"))]
        fks = [l.strip().rstrip(",") for l in lines if l.strip().upper().startswith("CONSTRAINT")]
        print(f"\n================ TABLE: `{t}` ================")
        print(f"Columns ({len(cols)}):")
        for c in cols:
            print(f"  {c}")
        if fks:
            print("Foreign Keys:")
            for fk in fks[:5]:
                print(f"  {fk}")
