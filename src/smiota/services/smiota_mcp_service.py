"""Smiota MCP Business Orchestration Service.

Enforces:
- Defense-in-depth authorization and customer tenant isolation.
- Validation of caller context from server-side session tokens.
- Safe mapping of Smiota Server API responses into standardized MCP Tool envelopes.
- Sensitive data isolation (no credentials or unredacted raw tokens returned).
- Distinction between empty results, auth required, not found, and transient errors.
"""
from typing import Any, Dict, List, Optional

from smiota.clients.smiota_api_client import SmiotaApiClient, get_smiota_api_client
from smiota.core.logging import logger, correlation_id_ctx
from smiota.mcp.context import CallerContext, get_caller_context
from smiota.mcp.errors import (
    McpAccessDeniedError,
    McpAuthenticationRequiredError,
    McpInvalidInputError,
    McpUnexpectedResponseError,
    McpUpstreamNotFoundError,
    McpUpstreamRateLimitedError,
    McpUpstreamServiceUnavailableError,
    McpUpstreamTimeoutError,
    SmiotaMcpError,
)
from smiota.schemas.mcp_tools import SmiotaToolResult, ToolResultCode


class SmiotaMcpService:
    """Orchestrates business operations for Smiota Model Context Protocol (MCP) tools."""

    def __init__(self, api_client: Optional[SmiotaApiClient] = None):
        self._api_client = api_client or get_smiota_api_client()

    def _get_active_caller(self, caller: Optional[CallerContext] = None) -> CallerContext:
        """Resolve caller context from explicit argument or ContextVar fallback."""
        ctx = caller or get_caller_context()
        if ctx is None:
            ctx = CallerContext(is_authenticated=False)
        return ctx

    def _get_cid(self, caller: CallerContext) -> Optional[str]:
        return caller.correlation_id or correlation_id_ctx.get()

    async def search_packages(
        self,
        status_group: str = "PENDING",
        status: Optional[str] = None,
        carrier: Optional[str] = None,
        storage_type: str = "ALL",
        days: Optional[int] = None,
        is_perishable: Optional[bool] = None,
        caller: Optional[CallerContext] = None,
    ) -> SmiotaToolResult:
        """Search and list authorized packages for the active resident."""
        resolved_caller = self._get_active_caller(caller)
        cid = self._get_cid(resolved_caller)

        if not resolved_caller.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to search_packages (session={resolved_caller.session_id})")
            return SmiotaToolResult.auth_required(correlation_id=cid)

        try:
            data = await self._api_client.search_packages(
                caller=resolved_caller,
                status_group=status_group,
                status=status,
                carrier=carrier,
                storage_type=storage_type,
                days=days,
                is_perishable=is_perishable,
            )

            packages = data.get("packages") or []
            if status:
                from smiota.schemas.package_status import normalize_status_key
                target_key = normalize_status_key(status)
                packages = [
                    p for p in packages
                    if normalize_status_key(p.get("status") or p.get("statusName")) == target_key
                ]
                data = dict(data)
                data["packages"] = packages
                data["total_count"] = len(packages)

            total_count = data.get("total_count", len(packages))

            if total_count == 0 or len(packages) == 0:
                filter_desc = f"status '{status}'" if status else f"status group '{status_group}'"
                return SmiotaToolResult.empty_result(
                    message=f"No packages found matching {filter_desc}" + (f" for carrier '{carrier}'" if carrier else "") + ".",
                    correlation_id=cid,
                )

            return SmiotaToolResult.success_result(
                data=data,
                message=f"Found {len(packages)} package(s) matching search criteria.",
                correlation_id=cid,
            )

        except McpAuthenticationRequiredError as err:
            return SmiotaToolResult.auth_required(message=err.message, correlation_id=cid)
        except McpAccessDeniedError as err:
            return SmiotaToolResult.error_result(ToolResultCode.ACCESS_DENIED, err.message, correlation_id=cid)
        except McpInvalidInputError as err:
            return SmiotaToolResult.invalid_input(err.message, missing_fields=err.missing_fields, correlation_id=cid)
        except McpUpstreamNotFoundError as err:
            return SmiotaToolResult.not_found(err.message, correlation_id=cid)
        except McpUpstreamRateLimitedError as err:
            return SmiotaToolResult.error_result(ToolResultCode.RATE_LIMITED, err.message, correlation_id=cid)
        except McpUpstreamTimeoutError as err:
            return SmiotaToolResult.error_result(
                ToolResultCode.UPSTREAM_TIMEOUT,
                "The package search request timed out. Please try again shortly.",
                correlation_id=cid,
            )
        except McpUpstreamServiceUnavailableError as err:
            return SmiotaToolResult.error_result(
                ToolResultCode.SERVICE_UNAVAILABLE,
                "Package retrieval service is currently unavailable. Please try again in a few moments.",
                correlation_id=cid,
            )
        except McpUnexpectedResponseError as err:
            return SmiotaToolResult.error_result(
                ToolResultCode.UNEXPECTED_RESPONSE,
                "Received an unexpected response from the package service.",
                correlation_id=cid,
            )
        except Exception as ex:
            logger.error(f"Unexpected internal error in search_packages: {ex}", exc_info=True)
            return SmiotaToolResult.error_result(
                ToolResultCode.INTERNAL_ERROR,
                "An unexpected error occurred while searching packages.",
                correlation_id=cid,
            )

    async def get_package_details(
        self,
        identifier: str,
        caller: Optional[CallerContext] = None,
    ) -> SmiotaToolResult:
        """Retrieve 360-degree attributes of a specific package."""
        resolved_caller = self._get_active_caller(caller)
        cid = self._get_cid(resolved_caller)

        if not resolved_caller.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to get_package_details for '{identifier}'")
            return SmiotaToolResult.auth_required(correlation_id=cid)

        cleaned_id = (identifier or "").strip()
        if not cleaned_id:
            return SmiotaToolResult.invalid_input("Package tracking number or identifier is required.", missing_fields=["identifier"], correlation_id=cid)

        import re
        if re.search(r"[\x00-\x1f\x7f;<>'\"`]|--|\bOR\b|\bAND\b|\bDROP\b|\bSELECT\b", cleaned_id, re.IGNORECASE):
            return SmiotaToolResult.invalid_input(
                f"Invalid identifier format '{cleaned_id}'. Identifier cannot contain control characters, quotes, or SQL operators.",
                missing_fields=["identifier"],
                correlation_id=cid,
            )

        try:
            data = await self._api_client.get_package_details(
                identifier=cleaned_id,
                caller=resolved_caller,
            )
            return SmiotaToolResult.success_result(
                data=data,
                message=f"Retrieved package details for '{cleaned_id}'.",
                correlation_id=cid,
            )

        except McpAuthenticationRequiredError as err:
            return SmiotaToolResult.auth_required(message=err.message, correlation_id=cid)
        except McpAccessDeniedError as err:
            return SmiotaToolResult.error_result(ToolResultCode.ACCESS_DENIED, err.message, correlation_id=cid)
        except McpInvalidInputError as err:
            return SmiotaToolResult.invalid_input(err.message, missing_fields=err.missing_fields, correlation_id=cid)
        except McpUpstreamNotFoundError:
            return SmiotaToolResult.not_found(
                f"We couldn't find any package matching tracking number or identifier '{cleaned_id}'.",
                correlation_id=cid,
            )
        except McpUpstreamRateLimitedError as err:
            return SmiotaToolResult.error_result(ToolResultCode.RATE_LIMITED, err.message, correlation_id=cid)
        except McpUpstreamTimeoutError:
            return SmiotaToolResult.error_result(
                ToolResultCode.UPSTREAM_TIMEOUT,
                f"The request to look up package '{cleaned_id}' timed out. Please try again.",
                correlation_id=cid,
            )
        except McpUpstreamServiceUnavailableError:
            return SmiotaToolResult.error_result(
                ToolResultCode.SERVICE_UNAVAILABLE,
                "Package retrieval service is currently unavailable. Please try again shortly.",
                correlation_id=cid,
            )
        except Exception as ex:
            logger.error(f"Unexpected internal error in get_package_details: {ex}", exc_info=True)
            return SmiotaToolResult.error_result(
                ToolResultCode.INTERNAL_ERROR,
                f"An unexpected error occurred while retrieving package '{cleaned_id}'.",
                correlation_id=cid,
            )

    async def get_package_timeline(
        self,
        identifier: str,
        caller: Optional[CallerContext] = None,
    ) -> SmiotaToolResult:
        """Retrieve audit timeline, dock scans, and chain-of-custody for a package."""
        resolved_caller = self._get_active_caller(caller)
        cid = self._get_cid(resolved_caller)

        if not resolved_caller.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to get_package_timeline for '{identifier}'")
            return SmiotaToolResult.auth_required(correlation_id=cid)

        cleaned_id = (identifier or "").strip()
        if not cleaned_id:
            return SmiotaToolResult.invalid_input("Package tracking number or identifier is required.", missing_fields=["identifier"], correlation_id=cid)

        import re
        if re.search(r"[\x00-\x1f\x7f;<>'\"`]|--|\bOR\b|\bAND\b|\bDROP\b|\bSELECT\b", cleaned_id, re.IGNORECASE):
            return SmiotaToolResult.invalid_input(
                f"Invalid identifier format '{cleaned_id}'. Identifier cannot contain control characters, quotes, or SQL operators.",
                missing_fields=["identifier"],
                correlation_id=cid,
            )

        try:
            data = await self._api_client.get_package_timeline(
                identifier=cleaned_id,
                caller=resolved_caller,
            )
            events = data.get("timeline") or data.get("chain_of_custody") or data.get("events") or []
            if events and "timeline" not in data:
                data["timeline"] = events
            if not events:
                return SmiotaToolResult.empty_result(
                    f"No timeline events recorded yet for package '{cleaned_id}'.",
                    correlation_id=cid,
                )
            return SmiotaToolResult.success_result(
                data=data,
                message=f"Retrieved {len(events)} timeline events for package '{cleaned_id}'.",
                correlation_id=cid,
            )

        except McpAuthenticationRequiredError as err:
            return SmiotaToolResult.auth_required(message=err.message, correlation_id=cid)
        except McpAccessDeniedError as err:
            return SmiotaToolResult.error_result(ToolResultCode.ACCESS_DENIED, err.message, correlation_id=cid)
        except McpUpstreamNotFoundError:
            return SmiotaToolResult.not_found(
                f"Package '{cleaned_id}' was not found in the tracking timeline repository.",
                correlation_id=cid,
            )
        except McpUpstreamTimeoutError:
            return SmiotaToolResult.error_result(
                ToolResultCode.UPSTREAM_TIMEOUT,
                f"Timeline lookup for package '{cleaned_id}' timed out.",
                correlation_id=cid,
            )
        except McpUpstreamServiceUnavailableError:
            return SmiotaToolResult.error_result(
                ToolResultCode.SERVICE_UNAVAILABLE,
                "Package timeline service is currently unavailable.",
                correlation_id=cid,
            )
        except Exception as ex:
            logger.error(f"Unexpected internal error in get_package_timeline: {ex}", exc_info=True)
            return SmiotaToolResult.error_result(
                ToolResultCode.INTERNAL_ERROR,
                f"An unexpected error occurred while retrieving timeline for '{cleaned_id}'.",
                correlation_id=cid,
            )

    async def get_user_preferences_and_services(
        self,
        caller: Optional[CallerContext] = None,
    ) -> SmiotaToolResult:
        """Retrieve user ADA accessibility preferences, authorized pickup proxies, and day-use pods."""
        resolved_caller = self._get_active_caller(caller)
        cid = self._get_cid(resolved_caller)

        if not resolved_caller.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to get_user_preferences_and_services")
            return SmiotaToolResult.auth_required(correlation_id=cid)

        try:
            data = await self._api_client.get_user_preferences_and_services(caller=resolved_caller)
            return SmiotaToolResult.success_result(
                data=data,
                message="Retrieved resident preferences, proxies, and locker services.",
                correlation_id=cid,
            )

        except McpAuthenticationRequiredError as err:
            return SmiotaToolResult.auth_required(message=err.message, correlation_id=cid)
        except McpAccessDeniedError as err:
            return SmiotaToolResult.error_result(ToolResultCode.ACCESS_DENIED, err.message, correlation_id=cid)
        except McpUpstreamTimeoutError:
            return SmiotaToolResult.error_result(
                ToolResultCode.UPSTREAM_TIMEOUT,
                "Preferences request timed out. Please try again.",
                correlation_id=cid,
            )
        except McpUpstreamServiceUnavailableError:
            return SmiotaToolResult.error_result(
                ToolResultCode.SERVICE_UNAVAILABLE,
                "User preferences service is currently unavailable.",
                correlation_id=cid,
            )
        except Exception as ex:
            logger.error(f"Unexpected internal error in get_user_preferences_and_services: {ex}", exc_info=True)
            return SmiotaToolResult.error_result(
                ToolResultCode.INTERNAL_ERROR,
                "An unexpected error occurred while retrieving user preferences.",
                correlation_id=cid,
            )

    async def get_my_pickup_pin(
        self,
        identifier: Optional[str] = None,
        caller: Optional[CallerContext] = None,
    ) -> SmiotaToolResult:
        """Retrieve active 6-digit pickup PIN and locker door verification for a delivery."""
        resolved_caller = self._get_active_caller(caller)
        cid = self._get_cid(resolved_caller)

        if not resolved_caller.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to get_my_pickup_pin (session={resolved_caller.session_id})")
            return SmiotaToolResult.auth_required(correlation_id=cid)

        try:
            if identifier:
                # Look up specific package
                pkg_result = await self.get_package_details(identifier=identifier, caller=resolved_caller)
                if not pkg_result.success:
                    return pkg_result

                pkg = pkg_result.data or {}
                passcode = pkg.get("passcode") or pkg.get("pickup_pin") or pkg.get("pin")
                loc = pkg.get("location") or {}
                door = loc.get("locker_door_name") or loc.get("door_number") or loc.get("locker_name") or "Locker Console"
                bank = loc.get("locker_bank") or "Main Pod Bank"
                building = loc.get("building_name") or "Main Facility"

                if not passcode:
                    return SmiotaToolResult.empty_result(
                        f"No active pickup PIN is currently assigned to package '{identifier}' (Status: {pkg.get('status', 'UNKNOWN')}).",
                        correlation_id=cid,
                    )

                return SmiotaToolResult.success_result(
                    data={
                        "package_id": pkg.get("id"),
                        "tracking_number": pkg.get("tracking_number"),
                        "pickup_pin": passcode,
                        "locker_door": door,
                        "locker_bank": bank,
                        "building": building,
                        "expiration_time": pkg.get("expiration_time"),
                        "instructions": f"Enter your 6-digit PIN {passcode} on the touchscreen console at {bank} ({building}). Door {door} will unlock automatically.",
                    },
                    message=f"Pickup PIN retrieved successfully for package '{identifier}'.",
                    correlation_id=cid,
                )
            else:
                # Look up active pending deliveries
                search_res = await self.search_packages(status_group="PENDING", caller=resolved_caller)
                if not search_res.success:
                    return search_res

                packages = (search_res.data or {}).get("packages", [])
                if not packages:
                    return SmiotaToolResult.empty_result(
                        "You do not have any pending packages awaiting pickup at this time.",
                        correlation_id=cid,
                    )

                pins = []
                for p in packages:
                    pin = p.get("passcode") or p.get("pickup_pin")
                    loc = p.get("location") or {}
                    door = loc.get("locker_door_name") or loc.get("door_number") or loc.get("locker_name") or "Locker Console"
                    bank = loc.get("locker_bank") or "Main Pod Bank"
                    if pin:
                        pins.append({
                            "tracking_number": p.get("tracking_number"),
                            "pickup_pin": pin,
                            "locker_door": door,
                            "locker_bank": bank,
                            "carrier": p.get("carrier"),
                            "expiration_time": p.get("expiration_time"),
                        })

                if not pins:
                    return SmiotaToolResult.empty_result(
                        "Your pending deliveries are currently being processed and do not have an active pickup PIN assigned yet.",
                        correlation_id=cid,
                    )

                primary = pins[0]
                return SmiotaToolResult.success_result(
                    data={
                        "total_pending_with_pin": len(pins),
                        "primary_pickup": primary,
                        "all_pickups": pins,
                        "instructions": f"Enter your 6-digit PIN on the touchscreen at {primary['locker_bank']}. Your compartment door ({primary['locker_door']}) will unlock.",
                    },
                    message=f"Retrieved pickup PINs for {len(pins)} delivery(ies).",
                    correlation_id=cid,
                )

        except Exception as ex:
            logger.error(f"Unexpected error in get_my_pickup_pin: {ex}", exc_info=True)
            return SmiotaToolResult.error_result(
                ToolResultCode.INTERNAL_ERROR,
                "Unable to retrieve pickup PIN at this time.",
                correlation_id=cid,
            )

    async def get_my_locker_details(
        self,
        identifier: Optional[str] = None,
        caller: Optional[CallerContext] = None,
    ) -> SmiotaToolResult:
        """Retrieve smart locker compartment location, bank name, and door number."""
        resolved_caller = self._get_active_caller(caller)
        cid = self._get_cid(resolved_caller)

        if not resolved_caller.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to get_my_locker_details")
            return SmiotaToolResult.auth_required(correlation_id=cid)

        try:
            if identifier:
                pkg_result = await self.get_package_details(identifier=identifier, caller=resolved_caller)
                if not pkg_result.success:
                    return pkg_result

                pkg = pkg_result.data or {}
                loc = pkg.get("location") or {}
                return SmiotaToolResult.success_result(
                    data={
                        "tracking_number": pkg.get("tracking_number"),
                        "storage_type": loc.get("storage_type", "LOCKER"),
                        "building_id": loc.get("building_id"),
                        "building_name": loc.get("building_name", "Main Facility"),
                        "locker_id": loc.get("locker_id"),
                        "locker_bank": loc.get("locker_bank", "Main Pod Bank"),
                        "locker_door_name": loc.get("locker_door_name") or loc.get("door_number") or "N/A",
                        "locker_size": loc.get("locker_size", "Medium"),
                        "status": pkg.get("status"),
                    },
                    message=f"Retrieved locker location details for package '{identifier}'.",
                    correlation_id=cid,
                )
            else:
                search_res = await self.search_packages(status_group="PENDING", caller=resolved_caller)
                if not search_res.success:
                    return search_res

                packages = (search_res.data or {}).get("packages", [])
                if not packages:
                    return SmiotaToolResult.empty_result(
                        "No active deliveries found in smart locker compartments for your account.",
                        correlation_id=cid,
                    )

                active_lockers = []
                for p in packages:
                    loc = p.get("location") or {}
                    active_lockers.append({
                        "tracking_number": p.get("tracking_number"),
                        "carrier": p.get("carrier"),
                        "storage_type": loc.get("storage_type", "LOCKER"),
                        "building_name": loc.get("building_name", "Main Facility"),
                        "locker_bank": loc.get("locker_bank", "Main Pod Bank"),
                        "locker_door_name": loc.get("locker_door_name") or loc.get("door_number") or "N/A",
                    })

                return SmiotaToolResult.success_result(
                    data={
                        "total_active_lockers": len(active_lockers),
                        "lockers": active_lockers,
                    },
                    message=f"Found {len(active_lockers)} active locker compartment(s) awaiting pickup.",
                    correlation_id=cid,
                )

        except Exception as ex:
            logger.error(f"Unexpected error in get_my_locker_details: {ex}", exc_info=True)
            return SmiotaToolResult.error_result(
                ToolResultCode.INTERNAL_ERROR,
                "Unable to retrieve locker details at this time.",
                correlation_id=cid,
            )


# Global singleton instance
_smiota_mcp_service_instance: Optional[SmiotaMcpService] = None


def get_smiota_mcp_service() -> SmiotaMcpService:
    """Retrieve shared SmiotaMcpService singleton."""
    global _smiota_mcp_service_instance
    if _smiota_mcp_service_instance is None:
        _smiota_mcp_service_instance = SmiotaMcpService()
    return _smiota_mcp_service_instance
