"""Export Smiota database schema DDL into a standalone SQL file."""
import os
import sys
import pymysql

DB_HOST = os.getenv("SMIOTA_DB_HOST", "10.128.15.219")
DB_PORT = int(os.getenv("SMIOTA_DB_PORT", "3306"))
DB_USER = os.getenv("SMIOTA_DB_USER", "usman-db-staging")
DB_PASS = os.getenv("SMIOTA_DB_PASSWORD", "UsmanStg@26!")
DB_NAME = os.getenv("SMIOTA_DB_NAME", "smiota")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smiota_schema.sql")


def export_ddl():
    print(f"Connecting to MySQL database '{DB_NAME}' at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            connect_timeout=15,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Failed to connect to database: {e}", file=sys.stderr)
        return False

    sql_output = [
        "-- ======================================================================",
        f"-- Smiota Database DDL Schema Export",
        f"-- Host: {DB_HOST}:{DB_PORT}",
        f"-- Database: {DB_NAME}",
        "-- ======================================================================",
        "\nSET FOREIGN_KEY_CHECKS = 0;\n"
    ]

    try:
        with conn.cursor() as cursor:
            # 1. Fetch all tables
            cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';")
            tables = cursor.fetchall()
            table_names = [list(r.values())[0] for r in tables]
            print(f"Found {len(table_names)} tables. Extracting DDL statements...")

            for tbl in table_names:
                cursor.execute(f"SHOW CREATE TABLE `{tbl}`;")
                res = cursor.fetchone()
                create_stmt = res.get("Create Table") or list(res.values())[1]
                sql_output.append(f"-- ----------------------------------------------------------------------")
                sql_output.append(f"-- Table structure for `{tbl}`")
                sql_output.append(f"-- ----------------------------------------------------------------------")
                sql_output.append(f"DROP TABLE IF EXISTS `{tbl}`;")
                sql_output.append(f"{create_stmt};\n")

            # 2. Fetch views (if any)
            cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW';")
            views = cursor.fetchall()
            if views:
                view_names = [list(r.values())[0] for r in views]
                print(f"Found {len(view_names)} views. Extracting view DDL...")
                for vw in view_names:
                    cursor.execute(f"SHOW CREATE VIEW `{vw}`;")
                    res = cursor.fetchone()
                    create_stmt = res.get("Create View") or list(res.values())[1]
                    sql_output.append(f"-- View structure for `{vw}`")
                    sql_output.append(f"{create_stmt};\n")

        sql_output.append("SET FOREIGN_KEY_CHECKS = 1;\n")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(sql_output))

        print(f"Successfully generated DDL SQL file at: {OUTPUT_FILE} ({len(table_names)} tables)")
        return True
    except Exception as e:
        print(f"Error while dumping DDL: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = export_ddl()
    sys.exit(0 if success else 1)
