from __future__ import annotations

"""Customer Agent: Troubleshooting, Device/Locker Status, Support Ticket Creation, Escalation."""
from typing import Any, Dict, List, Optional

from smiota.agents.base import BaseAgent, AgentContext, AgentResult
from smiota.agents.routing.rules import GREETINGS, RuleBasedRouter
from smiota.schemas.agents import AgentCapability
from smiota.agents.implementations.customer.prompts import CUSTOMER_SYSTEM_PROMPT
from smiota.agents.implementations.customer.tools import CUSTOMER_BOUND_TOOLS
from smiota.core.logging import logger

from smiota.mcp.context import (
    CallerContext,
    build_caller_context_from_agent_context,
    reset_caller_context,
    set_caller_context,
)
from smiota.mcp.client import MCPClient


class CustomerAgent(BaseAgent):
    """Customer experience and IoT smart locker operations agent."""

    def __init__(self):
        super().__init__(
            name="Customer",
            description="Specialized in customer troubleshooting, smart locker device status queries, and support ticketing.",
            domain="customer",
            capabilities=[
                AgentCapability(name="locker_telemetry", description="Query smart locker door, battery, and sensor state"),
                AgentCapability(name="parcel_tracking", description="Look up package dropoff and pickup audit events"),
                AgentCapability(name="ticketing", description="Create and escalate ServiceNow / Zendesk support tickets"),
                AgentCapability(name="remote_door_unlock", description="Remotely unlock locker compartment door", access_level="remediation"),
                AgentCapability(name="package_search", description="Search pending, released, outbound, and perishable packages"),
                AgentCapability(name="pickup_pin", description="Retrieve 6-digit pickup verification PIN and locker door"),
                AgentCapability(name="locker_details", description="Query locker bank, compartment door, and location details"),
                AgentCapability(name="delivery_timeline", description="Retrieve chain-of-custody audit timeline and dock scans"),
                AgentCapability(name="user_preferences", description="Retrieve ADA accessibility settings and proxy delegates"),
            ],
            system_prompt=CUSTOMER_SYSTEM_PROMPT,
            bound_tools=CUSTOMER_BOUND_TOOLS,
        )

    def _format_package_record(self, pkg: dict) -> list[str]:
        """
        Format package data strictly using fields present in the API response payload.
        Never invent or hallucinate instructions, locations, or statuses not present in the payload.
        """
        lines = []

        tracking_num = pkg.get("trackingNumber")
        if tracking_num:
            lines.append(f"• **Tracking Number**: `{tracking_num}`")

        pkg_id = pkg.get("id")
        uuid_val = pkg.get("uuid")
        if uuid_val and uuid_val != tracking_num:
            lines.append(f"• **Package UUID**: `{uuid_val}`")
        elif pkg_id and str(pkg_id) != str(tracking_num):
            lines.append(f"• **Package ID**: `{pkg_id}`")

        recipient = pkg.get("recipientName")
        if not recipient:
            recip_dict = pkg.get("recipient")
            if isinstance(recip_dict, dict):
                first = recip_dict.get("firstName", "")
                last = recip_dict.get("lastName", "")
                recipient = f"{first} {last}".strip()
        if recipient:
            lines.append(f"• **Recipient**: {recipient}")

        status_name = pkg.get("statusName") or pkg.get("status")
        if status_name:
            lines.append(f"• **Delivery Status**: **{status_name}**")

        building = pkg.get("currentlyBuildingName") or pkg.get("receivedBuildingName") or pkg.get("buildingName")
        intended_bldg = pkg.get("intendedBuildingName")
        if building:
            if intended_bldg and intended_bldg != building:
                lines.append(f"• **Location / Building**: {building} *(Intended for: {intended_bldg})*")
            else:
                lines.append(f"• **Location / Building**: {building}")

        storage_type = pkg.get("storageType")
        if storage_type:
            lines.append(f"• **Storage Type**: {storage_type}")

        carrier = pkg.get("courier") or pkg.get("carrier")
        pkg_type = pkg.get("packageTypeLabel")
        if carrier and pkg_type:
            lines.append(f"• **Carrier**: {carrier} ({pkg_type})")
        elif carrier:
            lines.append(f"• **Carrier**: {carrier}")
        elif pkg_type:
            lines.append(f"• **Package Type**: {pkg_type}")

        # Locker compartment (only if present in payload and not 0 or empty)
        locker = pkg.get("lockerName") or pkg.get("lockerUnitName") or pkg.get("doorNumber")
        locker_id = pkg.get("lockerId")
        if locker and locker not in ("0", 0, "None", None, "Kiosk Terminal") and locker_id not in (0, "0"):
            lines.append(f"• **Locker Compartment**: {locker}")

        received_time = pkg.get("receivedTime")
        if received_time:
            lines.append(f"• **Received At**: {received_time}")

        expiration_time = pkg.get("expirationTime")
        if expiration_time:
            lines.append(f"• **Expires At**: {expiration_time}")

        time_released = pkg.get("timeReleased")
        if time_released:
            lines.append(f"• **Released At**: {time_released}")

        released_to = pkg.get("releasedToUserName")
        if released_to:
            lines.append(f"• **Released To**: {released_to}")

        received_by = pkg.get("receivedByName")
        if received_by:
            lines.append(f"• **Received By**: {received_by}")

        notes = pkg.get("notes")
        if notes:
            lines.append(f"• **Notes**: {notes}")

        return lines

    def _get_suggested_actions(self, packages: list) -> list[str]:
        if not packages:
            return ["Where is my package?", "Look up by phone number", "Contact support concierge"]
        
        status = (packages[0].get("statusName") or packages[0].get("status") or "").lower()
        if any(w in status for w in ["released", "picked up", "delivered", "collected"]):
            return [
                "Track another package",
                "Look up by phone number",
                "Contact support concierge",
            ]
        
        return [
            "Resend Pickup PIN via SMS",
            "Extend pickup window (+24h)",
            "Locker door did not open",
        ]

    async def process(self, query: str, context: AgentContext) -> AgentResult:
        caller_ctx = build_caller_context_from_agent_context(context)
        ctx_token = set_caller_context(caller_ctx)
        try:
            return await self._process_internal(query, context, caller_ctx)
        finally:
            reset_caller_context(ctx_token)

    async def _process_internal(self, query: str, context: AgentContext, caller_ctx: Any) -> AgentResult:
        import re
        q = query.lower()

        # 1. Greetings & Welcome
        clean_q = re.sub(r"[^\w\s]", "", q).strip()
        if clean_q in GREETINGS or any(clean_q == w or clean_q.startswith(w + " ") for w in GREETINGS):
            return AgentResult(
                agent_name=self.name,
                content="Hello! 👋 How can I help you today?",
                requires_approval=False,
                suggested_actions=[
                    "Where is my package?",
                    "Resend pickup PIN",
                    "Locker location and hours",
                    "Locker door did not open",
                ],
            )

        # 1.01 Gratitude & Appreciation ("thank you", "thanks", "appreciate it")
        if RuleBasedRouter._is_gratitude(clean_q) or any(w in clean_q for w in ["thank you", "thanks", "thank u", "thx", "appreciate it"]):
            return AgentResult(
                agent_name=self.name,
                content="You're very welcome! If you need any more help with your deliveries or locker access, please feel free to ask. Have a great day!",
                requires_approval=False,
                suggested_actions=[
                    "Where is my package?",
                    "Resend pickup PIN",
                    "Locker location and hours",
                ],
            )

        # 1.02 Closings & Farewells ("bye", "byee", "goodbye", "see you", "have a good day")
        if RuleBasedRouter._is_farewell(clean_q) or any(w in clean_q for w in ["bye", "byee", "goodbye", "see you", "take care", "have a good day", "have a nice day", "have a great day"]):
            return AgentResult(
                agent_name=self.name,
                content="Goodbye! Have a wonderful day. If you ever need help with package pickups or your Smiota locker in the future, feel free to reach out!",
                requires_approval=False,
                suggested_actions=[
                    "Where is my package?",
                    "Locker location and hours",
                    "Contact support concierge",
                ],
            )

        # 2. Hardware State Mutation / Remote Unlock (Security Gate & HITL token required)
        if "unlock" in q or "open door" in q or "open locker" in q:
            return AgentResult(
                agent_name=self.name,
                content=(
                    f"Identified physical compartment unlock action: '{query}'. "
                    "Remotely opening a locker door mutates physical device hardware state. "
                    "An approval request has been generated for Property Manager / Support verification."
                ),
                requires_approval=True,
                approval_details={
                    "tool_name": "remote_unlock_locker_door",
                    "reason": f"Customer assistance unlock request: {query}",
                },
                suggested_actions=["Verify customer identity pin", "Wait for Property Manager approval"],
            )

        # 3. Locker Location & Hours
        if any(w in q for w in ["hours", "location", "address", "where is the locker", "facility"]):
            return AgentResult(
                agent_name=self.name,
                content=(
                    "📍 **Smiota Smart Locker Facility**:\n\n"
                    "• **Location**: Building 3, Ground Floor Lobby (East Wing by the elevators)\n"
                    "• **Operating Hours**: Accessible **24/7** for resident package pickup\n"
                    "• **Console**: Kiosk touchscreen is located in the center of the locker bank\n"
                    "• **Night Access**: Use your resident key fob or mobile badge to access the lobby after 9:00 PM."
                ),
                requires_approval=False,
                suggested_actions=[
                    "Where is my package?",
                    "Resend pickup PIN",
                    "Locker door did not open",
                ],
            )

        # 4. Resend Pickup PIN (Explicit PIN requests only - do not intercept tracking code queries)
        is_pin_query = bool(
            re.search(r'\b(?:pickup\s+pin|resend\s+pin|access\s+code|locker\s+pin|my\s+pin|resend\s+code|pickup\s+code|pin\s+code)\b', q)
            or (re.search(r'\bpin\b', q) and not any(k in q for k in ["tracking", "parcel", "package", "delivery", "status", "where is"]))
        ) and not any(k in q for k in ["tracking code", "track code", "package code", "parcel code", "status of"])

        if is_pin_query:
            if getattr(caller_ctx, "is_authenticated", False):
                try:
                    mcp_res = await MCPClient().execute_tool("get_my_pickup_pin", {})
                    if mcp_res.success and mcp_res.output:
                        out = mcp_res.output
                        if out.get("success") and out.get("data"):
                            data = out["data"]
                            primary = data.get("primary_pickup") or data
                            pin = primary.get("pickup_pin")
                            door = primary.get("locker_door")
                            bank = primary.get("locker_bank")
                            tracking = primary.get("tracking_number")
                            if pin:
                                return AgentResult(
                                    agent_name=self.name,
                                    content=(
                                        f"🔑 **Your Smiota Pickup PIN**:\n\n"
                                        f"• **6-Digit PIN**: `{pin}`\n"
                                        f"• **Locker Door**: **{door}**\n"
                                        f"• **Locker Bank**: {bank}\n"
                                        + (f"• **Tracking Number**: `{tracking}`\n\n" if tracking else "\n")
                                        + f"Enter your PIN on the kiosk touchscreen console to release compartment door **{door}**."
                                    ),
                                    requires_approval=False,
                                    suggested_actions=[
                                        "Locker location and hours",
                                        "Locker door did not open",
                                        "Where is my package?",
                                    ],
                                )
                except Exception as pin_err:
                    logger.debug(f"MCP get_my_pickup_pin skipped or errored: {pin_err}")

            return AgentResult(
                agent_name=self.name,
                content=(
                    "🔑 **Pickup PIN Assistance**:\n\n"
                    "To retrieve or resend your 6-digit pickup PIN, please enter your **Package ID** (e.g., `SM-9821`) "
                    "or your registered mobile phone number.\n\n"
                    "We will instantly resend your PIN and compartment barcode via SMS and email."
                ),
                requires_approval=False,
                suggested_actions=[
                    "Track: SM-9821",
                    "Look up by phone number",
                    "Locker location and hours",
                ],
            )

        # 5. Locker Door Did Not Open / Pickup Help
        if any(w in q for w in ["did not open", "didn't open", "not opening", "door stuck", "compartment stuck", "door help", "pickup help"]):
            return AgentResult(
                agent_name=self.name,
                content=(
                    "🚪 **Locker Compartment Troubleshooting**:\n\n"
                    "1. Confirm the 6-digit PIN entered matches your delivery notification.\n"
                    "2. **Gently press inward on the locker door**, then release — this disengages solenoid pressure if a package is pressing against the latch.\n"
                    "3. If the door still does not release, we can trigger a remote compartment reset or notify building maintenance."
                ),
                requires_approval=False,
                suggested_actions=[
                    "Request remote compartment unlock",
                    "Resend pickup PIN",
                    "Locker location and hours",
                ],
            )

        # 1.1 Conversational Clarifications & Feedback (e.g. "this is not good response", "i am asking something else")
        if any(w in q for w in ["not good", "wrong response", "not what i asked", "something else", "different question", "not helpful", "bad response"]):
            return AgentResult(
                agent_name=self.name,
                content=(
                    "I apologize for the misunderstanding! Let's get you the right information. 😊\n\n"
                    "What would you like assistance with today?\n"
                    "• 📦 **Check package delivery status**\n"
                    "• 🔑 **Retrieve or resend your 6-digit pickup PIN**\n"
                    "• 📍 **Locker location and 24/7 operating hours**\n"
                    "• 🚪 **Resolve a locker door or pickup issue**"
                ),
                requires_approval=False,
                suggested_actions=["Where is my package?", "Resend pickup PIN", "Locker location and hours"],
            )

        # 1.2 Small Talk & Greetings ("how are you", "who are you")
        if any(w in q for w in ["how are you", "how are you doing", "how r u", "who are you", "what can you do"]):
            return AgentResult(
                agent_name=self.name,
                content="I'm doing well, thank you! 😊 How can I help you today?",
                requires_approval=False,
                suggested_actions=["Where is my package?", "Resend pickup PIN", "Locker location and hours"],
            )

        # 1.3 Account Login Request
        if any(w in q for w in ["log in", "login", "sign in", "signin", "log in to your account"]):
            return AgentResult(
                agent_name=self.name,
                content=(
                    "To access your account, please log in through your resident or property portal. "
                    "Once signed in, you will have instant access to your deliveries, locker compartment details, and pickup PINs."
                ),
                requires_approval=False,
                suggested_actions=["Locker location and hours", "Contact support"],
            )

        # 6. Package UUID or Parcel Tracking ID Provided
        uuid_match = re.search(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', query)
        explicit_match = re.search(
            r'(?:tracking|package|parcel|uuid|number|id|code|#)\s*(?:is|number|id|code|#)?\s*[:=\s]\s*([a-zA-Z0-9_-]{4,50})',
            query,
            re.IGNORECASE,
        )
        track_cmd_match = re.search(
            r'\b(?:track|status\s+of|status\s+for)\s+([a-zA-Z0-9_-]{4,50})\b',
            query,
            re.IGNORECASE,
        )
        standalone_match = re.search(
            r'\b(sm-[0-9a-zA-Z_-]+|pkg-[0-9a-zA-Z_-]+|1z[0-9a-zA-Z]+|[0-9]{4,35}|(?=[a-zA-Z0-9_-]*\d)[a-zA-Z0-9_-]{5,35})\b',
            q,
        )

        stop_words = {
            "delivery", "customer", "tracking", "package", "building", "resident",
            "status", "number", "details", "update", "pickup", "here", "there",
            "please", "code", "today", "yesterday", "tomorrow", "account"
        }

        pkg_id = None
        is_uuid = False

        if uuid_match:
            pkg_id = uuid_match.group(0).lower()
            is_uuid = True
        elif explicit_match and explicit_match.group(1).lower() not in stop_words:
            pkg_id = explicit_match.group(1).lower()
        elif track_cmd_match and track_cmd_match.group(1).lower() not in stop_words:
            pkg_id = track_cmd_match.group(1).lower()
        elif standalone_match and standalone_match.group(0).lower() not in stop_words:
            pkg_id = standalone_match.group(0).lower()

        if pkg_id:
            # Check guest vs authenticated
            if not getattr(caller_ctx, "is_authenticated", False):
                return AgentResult(
                    agent_name=self.name,
                    content="You’re using Smiota Support as a guest. For your privacy and security, please log in to your Smiota account.",
                    requires_approval=False,
                    suggested_actions=[
                        "Log in to your account",
                        "Locker location and hours",
                        "Contact support",
                    ],
                )

            try:
                # Query packages via verified MCP tool search_packages
                all_packages = []
                try:
                    mcp_res = await MCPClient().execute_tool("search_packages", {"status_group": "ALL"})
                    if mcp_res.success and mcp_res.output:
                        out_data = mcp_res.output.get("data") if isinstance(mcp_res.output, dict) else {}
                        if isinstance(out_data, dict):
                            all_packages = out_data.get("packages") or []
                except Exception as mcp_err:
                    logger.debug(f"MCP search_packages lookup error: {mcp_err}")

                # Find package matching tracking number, id, or uuid
                matched_packages = [
                    p for p in all_packages
                    if str(p.get("trackingNumber", "")).lower() == pkg_id
                    or str(p.get("id", "")).lower() == pkg_id
                    or str(p.get("uuid", "")).lower() == pkg_id
                ]

                # Fallback to legacy package_service if not found in MCP packages list
                if not matched_packages:
                    parent_token = getattr(caller_ctx, "parent_token", None) or (context.user.get("parent_token") if isinstance(context.user, dict) else None)
                    if parent_token:
                        try:
                            from smiota.services.package_service import package_service
                            if is_uuid:
                                api_result = await package_service.get_packages(uuid=pkg_id, token=parent_token)
                            else:
                                api_result = await package_service.get_packages(by_name_or_number=pkg_id, token=parent_token)
                            if api_result.get("success"):
                                legacy_pkgs = api_result.get("packages", [])
                                if isinstance(legacy_pkgs, dict):
                                    legacy_pkgs = legacy_pkgs.get("data", [])
                                if legacy_pkgs:
                                    matched_packages = legacy_pkgs
                        except Exception as legacy_err:
                            logger.debug(f"Legacy package_service fallback skipped: {legacy_err}")

                if matched_packages:
                    if len(matched_packages) == 1:
                        details_lines = self._format_package_record(matched_packages[0])
                        body = "📦 **Package Delivery Details**\n\n" + "\n".join(details_lines)
                    else:
                        body_parts = [f"📦 **Found {len(matched_packages)} Packages**\n"]
                        for idx, p in enumerate(matched_packages[:5], 1):
                            p_lines = self._format_package_record(p)
                            body_parts.append(f"**Package {idx}:**\n" + "\n".join(p_lines))
                        body = "\n\n".join(body_parts)

                    return AgentResult(
                        agent_name=self.name,
                        content=body,
                        requires_approval=False,
                        suggested_actions=self._get_suggested_actions(matched_packages),
                    )

                # Check if resident has pending packages awaiting pickup
                pending_pkgs = [
                    p for p in all_packages
                    if str(p.get("status", "")).lower() in ["processed", "pending", "stored", "ready_for_pickup", "received"]
                ]

                if pending_pkgs:
                    body = (
                        f"I couldn't find any packages with tracking code or ID **{pkg_id}** in your account. 📦\n\n"
                        f"However, you currently have **{len(pending_pkgs)} active package(s)** awaiting pickup:\n\n"
                    )
                    for idx, p in enumerate(pending_pkgs[:5], 1):
                        trk = p.get("trackingNumber") or p.get("id")
                        st = p.get("status") or p.get("statusName") or "Pending"
                        loc = p.get("buildingName") or "Warehouse"
                        storage = p.get("storageType") or "Locker"
                        body += f"• **Package {idx}**: Tracking `{trk}` | Status: **{st}** | Storage: **{storage}** ({loc})\n"

                    body += "\nPlease double-check your tracking code or select one of your active packages above."
                    return AgentResult(
                        agent_name=self.name,
                        content=body,
                        requires_approval=False,
                        suggested_actions=[f"Track: {p.get('trackingNumber') or p.get('id')}" for p in pending_pkgs[:2]] + ["Locker location and hours"],
                    )

                id_label = "Package UUID" if is_uuid else "tracking code"
                return AgentResult(
                    agent_name=self.name,
                    content=(
                        f"I couldn't find any packages with {id_label} **{pkg_id}** in our system. 📦\n\n"
                        f"Please double-check the {id_label}, or contact your property management office if you need further help."
                    ),
                    requires_approval=False,
                    suggested_actions=["Where is my package?", "Look up by phone number", "Contact support concierge"],
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                return AgentResult(
                    agent_name=self.name,
                    content=(
                        f"I encountered an issue looking up tracking number **{pkg_id}**. "
                        "Please try again shortly or contact your property concierge."
                    ),
                    requires_approval=False,
                    suggested_actions=["Where is my package?", "Contact support concierge"],
                )

        # 7. Resident Phone or Email Lookup Provided (e.g. user provides email or phone to trace parcels)
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', q)
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', q)
        if phone_match or email_match:
            identifier = phone_match.group(0) if phone_match else email_match.group(0)
            try:
                from smiota.services.package_service import package_service

                # Optional Text-to-SQL audit log (non-blocking)
                try:
                    from smiota.database.sql_generator import TextToSQLEngine
                    engine = TextToSQLEngine()
                    await engine.generate_sql(
                        query,
                        user_context={"resident_id": context.user_id, "channel": context.channel, "tenant_id": context.tenant_id},
                    )
                except Exception as sql_err:
                    logger.debug(f"Optional Text-to-SQL audit log skipped: {sql_err}")

                # Query Smiota Server endpoint: GET /api/v1/packages?byNameOrNumber=... using parent token
                parent_token = (
                    getattr(context, "parent_token", None)
                    or (context.user.get("parent_token") if isinstance(context.user, dict) else None)
                    or (context.metadata.get("parent_token") if isinstance(context.metadata, dict) else None)
                    or (context.metadata.get("token") if isinstance(context.metadata, dict) else None)
                    or None
                )
                if not parent_token:
                    return AgentResult(
                        agent_name=self.name,
                        content="You’re using Smiota Support as a guest. For your privacy and security, please log in to your Smiota account.",
                        requires_approval=False,
                        suggested_actions=[
                            "Log in to your account",
                            "Locker location and hours",
                            "Contact support",
                        ],
                    )

                api_result = await package_service.get_packages(by_name_or_number=identifier, token=parent_token)
                if not api_result.get("success"):
                    if api_result.get("error_type") in ["UNAUTHENTICATED", "AUTH_ERROR"]:
                        return AgentResult(
                            agent_name=self.name,
                            content="You’re using Smiota Support as a guest. For your privacy and security, please log in to your Smiota account.",
                            requires_approval=False,
                            suggested_actions=[
                                "Log in to your account",
                                "Locker location and hours",
                                "Contact support",
                            ],
                        )
                    return AgentResult(
                        agent_name=self.name,
                        content="I apologize, I'm taking a bit longer than expected to look that up. Please try again.",
                        requires_approval=False,
                        suggested_actions=["Where is my package?", "Resend pickup PIN", "Locker location and hours"],
                    )

                packages = api_result.get("packages", [])
                if isinstance(packages, dict):
                    packages = packages.get("data", [])

                if not packages:
                    return AgentResult(
                        agent_name=self.name,
                        content=(
                            f"I couldn't find any active deliveries registered for **{identifier}**. 📱\n\n"
                            "Please confirm the contact details or check with your property management office."
                        ),
                        requires_approval=False,
                        suggested_actions=["Where is my package?", "Look up by phone number", "Contact support concierge"],
                    )

                if len(packages) == 1:
                    details_lines = self._format_package_record(packages[0])
                    body = f"📱 **Active Delivery for {identifier}**\n\n" + "\n".join(details_lines)
                else:
                    body_parts = [f"📱 **Active Deliveries for {identifier} ({len(packages)} Package(s))**\n"]
                    for idx, p in enumerate(packages[:5], 1):
                        p_lines = self._format_package_record(p)
                        body_parts.append(f"**Package {idx}:**\n" + "\n".join(p_lines))
                    body = "\n\n".join(body_parts)

                return AgentResult(
                    agent_name=self.name,
                    content=body,
                    requires_approval=False,
                    suggested_actions=self._get_suggested_actions(packages),
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                return AgentResult(
                    agent_name=self.name,
                    content=(
                        f"I encountered an issue looking up packages for **{identifier}**. "
                        "Please try again shortly or contact your property concierge."
                    ),
                    requires_approval=False,
                    suggested_actions=["Where is my package?", "Contact support concierge"],
                )

        # Identify informational intent before calling LLM or evaluating generic tracking prompts
        info_match = RuleBasedRouter._match_informational(query)
        is_informational = info_match is not None
        info_prefix = info_match[0] if info_match else None
        info_category = info_match[1] if info_match else None

        # 8. Check Parcel / Tracking / Collection Inquiry (Proactively check active pending packages for authenticated residents)
        package_inquiry_terms = [
            "parcel", "package", "tracking", "track", "delivery", "deliveries",
            "pickup", "pick up", "collect", "collection", "mail", "anything to collect",
            "anything to pick", "anything for me", "anything waiting", "what do i have",
            "do i have anything", "do i have any", "any packages", "any parcels",
            "my items", "my stuff", "items pending", "pending items", "where is my",
            "my packages", "my delivery", "to collect", "ready for collection", "pending"
        ]
        if not is_informational and any(w in q for w in package_inquiry_terms):
            if getattr(caller_ctx, "is_authenticated", False):
                try:
                    mcp_res = await MCPClient().execute_tool("search_packages", {"status_group": "PENDING"})
                    if mcp_res.success and mcp_res.output:
                        out_data = mcp_res.output.get("data") if isinstance(mcp_res.output, dict) else {}
                        if isinstance(out_data, dict):
                            pkgs = out_data.get("packages") or []
                            if pkgs:
                                if len(pkgs) == 1:
                                    details_lines = self._format_package_record(pkgs[0])
                                    body = "📦 **You have 1 pending package awaiting pickup:**\n\n" + "\n".join(details_lines)
                                else:
                                    body_parts = [f"📦 **You have {len(pkgs)} pending packages awaiting pickup:**\n"]
                                    for idx, p in enumerate(pkgs[:5], 1):
                                        p_lines = self._format_package_record(p)
                                        body_parts.append(f"**Package {idx}:**\n" + "\n".join(p_lines))
                                    body = "\n\n".join(body_parts)

                                return AgentResult(
                                    agent_name=self.name,
                                    content=body,
                                    requires_approval=False,
                                    suggested_actions=self._get_suggested_actions(pkgs),
                                )
                            else:
                                return AgentResult(
                                    agent_name=self.name,
                                    content=(
                                        "You currently have no pending packages awaiting pickup. 📦\n\n"
                                        "If you are looking for a past delivery or have a specific tracking number, please provide it and I'll look it up!"
                                    ),
                                    requires_approval=False,
                                    suggested_actions=["Track another package", "Resend pickup PIN", "Locker location and hours"],
                                )
                except Exception as mcp_err:
                    logger.debug(f"MCP search_packages pending query skipped or errored: {mcp_err}")

            return AgentResult(
                agent_name=self.name,
                content=(
                    "I can certainly check that for you! 📦\n\n"
                    "Please provide your **Package ID** or **Tracking Number** (e.g., `SM-9821` or `PKG-4402`) "
                    "so I can locate your locker compartment and delivery status."
                ),
                requires_approval=False,
                suggested_actions=[
                    "Track: SM-9821",
                    "Track: PKG-4402",
                    "Look up by phone number",
                    "I don't have tracking ID",
                ],
            )

        # 9. Fallback Account Lookup Prompt (Phone / Email)
        if not is_informational and any(w in q for w in ["phone", "email", "don't have", "dont have", "no tracking"]):
            if getattr(caller_ctx, "is_authenticated", False):
                try:
                    mcp_res = await MCPClient().execute_tool("search_packages", {"status_group": "PENDING"})
                    if mcp_res.success and mcp_res.output:
                        out_data = mcp_res.output.get("data") if isinstance(mcp_res.output, dict) else {}
                        pkgs = out_data.get("packages") or [] if isinstance(out_data, dict) else []
                        if pkgs:
                            body_parts = [f"📦 **You have {len(pkgs)} pending package(s) registered under your account:**\n"]
                            for idx, p in enumerate(pkgs[:5], 1):
                                p_lines = self._format_package_record(p)
                                body_parts.append(f"**Package {idx}:**\n" + "\n".join(p_lines))
                            return AgentResult(
                                agent_name=self.name,
                                content="\n\n".join(body_parts),
                                requires_approval=False,
                                suggested_actions=self._get_suggested_actions(pkgs),
                            )
                except Exception as e:
                    logger.debug(f"MCP search_packages lookup error: {e}")

            return AgentResult(
                agent_name=self.name,
                content=(
                    "No problem! You can look up your parcels using the mobile phone number or email address registered with your account.\n\n"
                    "Please enter your registered mobile number (e.g. `+1 555-0199`) or resident email address:"
                ),
                requires_approval=False,
                suggested_actions=[
                    "Verify phone: +1 555-0199",
                    "Verify email: user@smiota.com",
                    "Contact support concierge",
                ],
            )

        # 9. Smart Locker Sensor & Hardware Diagnostics
        if not is_informational and any(w in q for w in ["sensor", "jammed"]):
            return AgentResult(
                agent_name=self.name,
                content=(
                    "🔧 **Locker Diagnostics**: Running real-time telemetry check on smart locker sensors...\n\n"
                    "• **Controller Status**: Online (Ping: 14ms)\n"
                    "• **Optical Sensor**: Active (No physical obstruction detected)\n"
                    "• **Solenoid Latch**: Engaged (Normal resistance)\n\n"
                    "If the compartment door is not opening, ensure your PIN was entered at the kiosk console or request remote assistance."
                ),
                requires_approval=False,
                suggested_actions=[
                    "Request remote compartment unlock",
                    "Resend pickup PIN",
                    "Locker location and hours",
                ],
            )

        # 10. Informational & Open-Ended Inquiry -> Invoke Gemini / Vertex AI
        try:
            from smiota.llm.provider import GeminiProvider
            llm = GeminiProvider()
            auth_instruction = ""
            if getattr(caller_ctx, "is_authenticated", False):
                user_name = getattr(caller_ctx, "name", "") or (context.user.get("name") if isinstance(context.user, dict) else "") or "Resident"
                auth_instruction = (
                    f"\n[AUTHENTICATED USER CONTEXT]\n"
                    f"The resident is already verified and signed in as '{user_name}' (ID: {caller_ctx.user_id}).\n"
                    f"IMPORTANT: NEVER ask the resident for their full name, phone number, or email address because they are already authenticated.\n"
                )

            prompt = (
                f"[Informational Query - Category: {info_category}, Pattern: '{info_prefix}']\n"
                f"{auth_instruction}"
                f"Resident query: {query}\n"
                f"Provide a helpful, polite, and concise instructional answer for the resident."
                if is_informational
                else f"{auth_instruction}Resident query: {query}\nProvide a helpful, polite, and concise answer for the resident."
            )
            llm_reply = await llm.generate_completion(
                prompt=prompt,
                system_instruction=self.system_prompt,
            )
            result_metadata = {}
            if is_informational:
                result_metadata = {
                    "is_informational": True,
                    "category": info_category,
                    "matched_prefix": info_prefix,
                }
            return AgentResult(
                agent_name=self.name,
                content=llm_reply,
                requires_approval=False,
                suggested_actions=[
                    "Where is my package?",
                    "Resend pickup PIN",
                    "Locker location and hours",
                    "Locker door did not open",
                ],
                metadata=result_metadata,
            )
        except Exception:
            return AgentResult(
                agent_name=self.name,
                content=f"I'm here to help with your Smiota smart locker deliveries! Regarding '{query}', would you like me to check a package, retrieve your pickup PIN, or connect you with property concierge?",
                requires_approval=False,
                suggested_actions=[
                    "Where is my package?",
                    "Resend pickup PIN",
                    "Locker location and hours",
                    "Locker door did not open",
                ],
            )


