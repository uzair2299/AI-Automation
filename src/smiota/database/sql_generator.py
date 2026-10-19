"""Dynamic Text-to-SQL Engine using Smiota Core Schema and Vertex AI Gemini.

Translates natural language resident and parcel queries into safe,
read-only MySQL 8.x queries against the Smiota database schema.
"""
import re
from typing import Any, Dict, List, Optional
from smiota.core.logging import logger
from smiota.database.core_schema import CORE_CUSTOMER_SCHEMA_PROMPT
from smiota.llm.provider import GeminiProvider


TEXT_TO_SQL_SYSTEM_INSTRUCTION = f"""You are the Smiota Smart Locker Database Expert and Text-to-SQL Generator.
Given a user's natural language question, your job is to generate a precise, read-only MySQL 8.x SQL query.

{CORE_CUSTOMER_SCHEMA_PROMPT}

RULES:
1. ONLY generate a single valid MySQL SELECT query.
2. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE statements.
3. Always include `p.is_deleted = 0` when querying the `package` table.
4. When tracking numbers are referenced, match on `package.tracking_number`.
5. When resident phone or email is referenced, join `user u ON p.RECIPIENT_ID = u.ID` and filter on `u.PHONE` or `u.EMAIL`.
6. Always JOIN `locker l ON p.LOCKER_ID = l.ID` to get the compartment name (`l.NAME`), door sensor (`l.IS_GATE_OPEN`), and fault flag (`l.IS_IN_ERROR_STATE`).
7. Always JOIN `building b ON p.currently_at_building_id = b.ID` to get the physical building name.
8. If the query does not have a LIMIT clause, end with `LIMIT 10;`.
9. OUTPUT FORMAT: Return ONLY the raw SQL statement. Do not add explanations or conversational filler.
"""


DANGEROUS_SQL_PATTERNS = [
    r"\b(insert|update|delete|drop|alter|truncate|create|replace|grant|revoke)\b",
    r"\b(exec|execute|union\s+all\s+select|load_file|into\s+outfile|into\s+dumpfile)\b",
    r";\s*\w+",  # Chained multiple queries
]


class TextToSQLEngine:
    """Generates and validates read-only SQL queries from natural language."""

    def __init__(self):
        self.llm = GeminiProvider()

    def validate_sql(self, sql: str) -> str:
        """Validate that the query is safe, read-only, and well-formed."""
        cleaned_sql = sql.strip()

        # Remove markdown code fences if model returned them
        if cleaned_sql.startswith("```"):
            cleaned_sql = re.sub(r"^```(?:sql)?\s*", "", cleaned_sql, flags=re.IGNORECASE)
            cleaned_sql = re.sub(r"\s*```$", "", cleaned_sql)
            cleaned_sql = cleaned_sql.strip()

        # Ensure query begins with SELECT or WITH (for CTEs)
        if not re.match(r"^(SELECT|WITH)\b", cleaned_sql, re.IGNORECASE):
            raise ValueError(f"Security Alert: Only SELECT queries are permitted. Got: '{cleaned_sql[:30]}...'")

        # Check for forbidden mutation keywords
        for pattern in DANGEROUS_SQL_PATTERNS:
            match = re.search(pattern, cleaned_sql, re.IGNORECASE)
            if match:
                raise ValueError(f"Security Alert: Forbidden SQL keyword detected ('{match.group(0)}')")

        # Ensure a reasonable LIMIT clause exists
        if not re.search(r"\bLIMIT\s+\d+", cleaned_sql, re.IGNORECASE):
            cleaned_sql = cleaned_sql.rstrip(";") + " LIMIT 10;"

        return cleaned_sql

    async def generate_sql(self, natural_language_query: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Generate safe MySQL SELECT statement using Vertex AI Gemini."""
        prompt = f"User Request: {natural_language_query}"
        if user_context:
            context_str = ", ".join(f"{k}={v}" for k, v in user_context.items() if v)
            if context_str:
                prompt += f"\nActive User Context: {context_str}"

        raw_sql = await self.llm.generate_completion(
            prompt=prompt,
            system_instruction=TEXT_TO_SQL_SYSTEM_INSTRUCTION,
            temperature=0.0,
        )

        validated_sql = self.validate_sql(raw_sql)

        # 1. High-visibility terminal / console banner (ASCII safe for all terminals)
        log_banner = (
            "\n"
            + "=" * 80 + "\n"
            + ">> [SMIOTA TEXT-TO-SQL] DYNAMIC QUERY GENERATED (CORE SCHEMA)\n"
            + f">> Resident Query: {natural_language_query}\n"
            + "-" * 80 + "\n"
            + f"{validated_sql}\n"
            + "=" * 80
        )
        logger.info(log_banner)

        # 2. Append comprehensive transaction record to dedicated log file: logs/text_to_sql.log
        try:
            import os
            from datetime import datetime
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "text_to_sql.log")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ctx_summary = ", ".join(f"{k}={v}" for k, v in user_context.items() if v) if user_context else "None"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] ========================================================\n")
                f.write(f"USER QUERY       : {natural_language_query}\n")
                f.write(f"USER CONTEXT     : {ctx_summary}\n")
                f.write(f"MODEL / ENGINE   : Vertex AI [{self.llm.model_name}] (Core Schema Prompt)\n")
                f.write(f"GENERATED SQL    :\n{validated_sql}\n")
                f.write(f"VALIDATION STATUS: PASS (Read-only SELECT, LIMIT enforced)\n")
                f.write("------------------------------------------------------------------------\n")
        except Exception as log_err:
            logger.warning(f"Could not append to text_to_sql.log: {log_err}")

        return validated_sql

    async def synthesize_answer(
        self,
        user_query: str,
        sql: str,
        rows: List[Dict[str, Any]],
    ) -> str:
        """Format database query results into a concise, friendly resident message."""
        system_instruction = (
            "You are the Smiota Smart Locker Concierge. "
            "Given the user's question, the SQL query executed, and the database records found, "
            "provide a helpful, friendly, and concise answer. "
            "Highlight the Locker compartment number, pickup PIN (PASSCODE), carrier name, and building location. "
            "If no packages were found, politely inform the user and suggest checking their tracking number or registered phone."
        )

        prompt = (
            f"User Question: {user_query}\n"
            f"Executed SQL: {sql}\n"
            f"Database Results (Total records: {len(rows)}):\n"
            f"{rows}\n\n"
            "Format the concierge response for the resident:"
        )

        response = await self.llm.generate_completion(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.2,
        )
        return response
