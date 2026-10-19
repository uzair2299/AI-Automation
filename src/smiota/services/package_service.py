"""Smiota Server REST Client for Package Tracking & Status.

Communicates with Smiota Server endpoint:
GET /api/v1/packages?byNameOrNumber=<tracking_or_name>
Authorization: Bearer <token>
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx
from smiota.core.config import get_settings
from smiota.core.logging import logger


class SmiotaPackageService:
    """Client for Smiota Server package status and tracking APIs."""

    def __init__(self):
        self.settings = get_settings()

    @property
    def base_url(self) -> str:
        return os.environ.get("SMIOTA_SERVER_BASE_URL") or getattr(
            self.settings, "SMIOTA_SERVER_BASE_URL", "http://localhost:8080"
        )

    @property
    def default_token(self) -> str:
        return os.environ.get("SAVED_SESSION_TOKEN") or getattr(
            self.settings, "SAVED_SESSION_TOKEN", "350ab6f7-7dfb-468c-a68a-f7b150b489f3"
        )

    def _log_api_call(self, url: str, params: dict, status: str, details: str) -> None:
        """Log API request details to logs/text_to_sql.log and logs/smiota.log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"\n[{timestamp}] --- [SMIOTA SERVER API CALL] ---\n"
            f"ENDPOINT   : GET {url}\n"
            f"PARAMS     : {params}\n"
            f"AUTH TOKEN : Bearer {self.default_token[:8]}...{self.default_token[-6:]}\n"
            f"STATUS     : {status}\n"
            f"DETAILS    : {details}\n"
            f"------------------------------------------------------------------------\n"
        )
        logger.info(log_entry)
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            log_file = os.path.join(base_dir, "logs", "text_to_sql.log")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

    @staticmethod
    def is_uuid(value: Optional[str]) -> bool:
        """Check if a string matches standard RFC-4122 UUID format (8-4-4-4-12 hex)."""
        if not value:
            return False
        import re
        return bool(re.match(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", str(value).strip()))

    async def get_packages(
        self,
        by_name_or_number: Optional[str] = None,
        uuid: Optional[str] = None,
        status_id: Optional[int] = None,
        pagenumber: int = 1,
        pagesize: int = 10,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch package details from Smiota Server GET /api/v1/packages using URL query parameters."""
        auth_token = token or self.default_token
        url = f"{self.base_url.rstrip('/')}/api/v1/packages"

        params: Dict[str, Any] = {
            "token": auth_token,
            "pagenumber": pagenumber,
            "pagesize": pagesize,
        }
        if by_name_or_number:
            if self.is_uuid(by_name_or_number):
                params["uuid"] = by_name_or_number.strip()
            else:
                params["byNameOrNumber"] = by_name_or_number
        if uuid:
            params["uuid"] = uuid.strip()
        if status_id is not None:
            params["statusId"] = status_id

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "token": auth_token,
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    payload = response.json()
                    packages: List[Dict[str, Any]] = []
                    total_records = 0
                    if isinstance(payload, dict):
                        data_node = payload.get("data")
                        if isinstance(data_node, dict):
                            packages = data_node.get("data", [])
                            total_records = data_node.get("totalRecords", len(packages))
                        elif isinstance(data_node, list):
                            packages = data_node
                            total_records = len(packages)
                        else:
                            packages = []
                            total_records = 0
                    elif isinstance(payload, list):
                        packages = payload
                        total_records = len(packages)

                    self._log_api_call(
                        url,
                        params,
                        f"HTTP 200 OK ({len(packages)} package(s) returned, totalRecords={total_records})",
                        f"Result: {packages}",
                    )
                    return {"success": True, "packages": packages, "totalRecords": total_records}
                elif response.status_code == 401:
                    err_msg = "Smiota server authentication failed (HTTP 401 Unauthorized). The session token is expired or invalid."
                    self._log_api_call(url, params, "HTTP 401 UNAUTHORIZED", f"Response: {response.text[:200]}")
                    return {"success": False, "error_type": "AUTH_ERROR", "message": err_msg}
                else:
                    err_msg = f"Smiota server returned HTTP {response.status_code}."
                    self._log_api_call(url, params, f"HTTP {response.status_code}", f"Response: {response.text[:200]}")
                    return {"success": False, "error_type": f"HTTP_{response.status_code}", "message": err_msg}
        except Exception as e:
            err_msg = f"Unable to reach Smiota server at {self.base_url} ({e})."
            self._log_api_call(url, params, "CONNECTION_ERROR", err_msg)
            return {"success": False, "error_type": "CONNECTION_ERROR", "message": err_msg}


package_service = SmiotaPackageService()
