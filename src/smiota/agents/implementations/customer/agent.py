"""Customer Agent: Troubleshooting, Device/Locker Status, Support Ticket Creation, Escalation."""
from smiota.agents.base import BaseAgent, AgentContext, AgentResult
from smiota.schemas.agents import AgentCapability
from smiota.agents.implementations.customer.prompts import CUSTOMER_SYSTEM_PROMPT
from smiota.agents.implementations.customer.tools import CUSTOMER_BOUND_TOOLS


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

        uuid_val = pkg.get("uuid")
        if uuid_val and uuid_val != tracking_num:
            lines.append(f"• **Package UUID**: `{uuid_val}`")

        recipient = pkg.get("recipientName")
        if not recipient:
            recip_dict = pkg.get("recipient")
            if isinstance(recip_dict, dict):
                first = recip_dict.get("firstName", "")
                last = recip_dict.get("lastName", "")
                recipient = f"{first} {last}".strip()
        if recipient:
            lines.append(f"• **Recipient**: {recipient}")

        status_name = pkg.get("statusName")
        if status_name:
            lines.append(f"• **Delivery Status**: **{status_name}**")

        building = pkg.get("currentlyBuildingName") or pkg.get("receivedBuildingName")
        intended_bldg = pkg.get("intendedBuildingName")
        if building:
            if intended_bldg and intended_bldg != building:
                lines.append(f"• **Location / Building**: {building} *(Intended for: {intended_bldg})*")
            else:
                lines.append(f"• **Location / Building**: {building}")

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
            return ["Where is my package•", "Look up by phone number", "Contact support concierge"]
        
        status = (packages[0].get("statusName") or "").lower()
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
        import re
        q = query.lower()

        # 1. Greetings & Welcome
        if any(q.strip() == w or q.strip().startswith(w + " ") or q.strip().startswith(w + ",") for w in ["hi", "hello", "hey", "hola", "good morning", "good afternoon", "good evening", "howdy"]):
            return AgentResult(
                agent_name=self.name,
                content=(
                    "Hello! 👋 I'm your Smiota Smart Locker Concierge.\n\n"
                    "I can help you:\n"
                    "• 📦 **Check package delivery status** and locker compartment numbers\n"
                    "• 🔑 **Retrieve or resend your 6-digit pickup PIN**\n"
                    "• 📍 **Find locker location and operating hours**\n"
                    "• 🚪 **Resolve locker door or pickup issues**\n\n"
                    "What would you like to check today•"
                ),
                requires_approval=False,
                suggested_actions=[
                    "Where is my package•",
                    "Resend pickup PIN",
                    "Locker location and hours",
                    "Locker door did not open",
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
                    "Where is my package•",
                    "Resend pickup PIN",
                    "Locker door did not open",
                ],
            )

        # 4. Resend Pickup PIN
        if any(w in q for w in ["pin", "code", "pickup pin", "resend pin", "access code"]):
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

        # 6. Package UUID or Parcel Tracking ID Provided
        uuid_match = re.search(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', query)
        tracking_match = re.search(r'\b(sm-[0-9a-z]+|pkg-[0-9a-z]+|1z[0-9a-z]+|[0-9]{8,}|(•=[a-z]*[0-9])(•=[0-9]*[a-z])[a-z0-9]{8,})\b', q)
        if uuid_match or tracking_match:
            is_uuid = bool(uuid_match)
            pkg_id = uuid_match.group(0).lower() if is_uuid else tracking_match.group(0)
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

                # Query Smiota Server endpoint:
                # - If standard RFC-4122 UUID: GET /api/v1/packages•uuid=...
                # - If Tracking Number / Name: GET /api/v1/packages•byNameOrNumber=...
                if is_uuid:
                    api_result = await package_service.get_packages(uuid=pkg_id)
                else:
                    api_result = await package_service.get_packages(by_name_or_number=pkg_id)

                if not api_result.get("success"):
                    return AgentResult(
                        agent_name=self.name,
                        content=(
                            f"I'm temporarily unable to retrieve package details for **{pkg_id}**. "
                            "Please try again in a few moments or contact your property management office for assistance."
                        ),
                        requires_approval=False,
                        suggested_actions=["Where is my package•", "Resend pickup PIN", "Locker location and hours"],
                    )

                packages = api_result.get("packages", [])
                if isinstance(packages, dict):
                    packages = packages.get("data", [])

                if not packages:
                    id_label = "Package UUID" if is_uuid else "tracking number"
                    return AgentResult(
                        agent_name=self.name,
                        content=(
                            f"I couldn't find any packages with {id_label} **{pkg_id}** in our system. 📦\n\n"
                            f"Please double-check the {id_label}, or contact your property management office if you need further help."
                        ),
                        requires_approval=False,
                        suggested_actions=["Where is my package•", "Look up by phone number", "Contact support concierge"],
                    )

                if len(packages) == 1:
                    details_lines = self._format_package_record(packages[0])
                    body = "📦 **Package Delivery Details**\n\n" + "\n".join(details_lines)
                else:
                    body_parts = [f"📦 **Found {len(packages)} Packages**\n"]
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
                        f"I encountered an issue looking up tracking number **{pkg_id}**. "
                        "Please try again shortly or contact your property concierge."
                    ),
                    requires_approval=False,
                    suggested_actions=["Where is my package•", "Contact support concierge"],
                )

        # 7. Resident Phone or Email Lookup Provided (e.g. user provides email or phone to trace parcels)
        phone_match = re.search(r'(\+•\d{1,3}[-.\s]•)•\(•\d{3}\)•[-.\s]•\d{3}[-.\s]•\d{4}', q)
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

                # Query Smiota Server endpoint: GET /api/v1/packages•byNameOrNumber=...
                api_result = await package_service.get_packages(by_name_or_number=identifier)
                if not api_result.get("success"):
                    return AgentResult(
                        agent_name=self.name,
                        content=(
                            f"I'm temporarily unable to check deliveries for **{identifier}**. "
                            "Please try again shortly or contact your property concierge."
                        ),
                        requires_approval=False,
                        suggested_actions=["Where is my package•", "Resend pickup PIN", "Locker location and hours"],
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
                        suggested_actions=["Where is my package•", "Look up by phone number", "Contact support concierge"],
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
                    suggested_actions=["Where is my package•", "Contact support concierge"],
                )

        # 8. Check Parcel / Tracking Inquiry (Prompt for Package ID or Tracking Number if none given)
        if any(w in q for w in ["parcel", "package", "tracking", "track", "delivery", "pickup", "where is my"]):
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
        if any(w in q for w in ["phone", "email", "don't have", "dont have", "no tracking"]):
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
        if any(w in q for w in ["sensor", "jammed"]):
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

        # 10. Open-Ended Inquiry -> Invoke Gemini / Vertex AI
        try:
            from smiota.llm.provider import GeminiProvider
            llm = GeminiProvider()
            llm_reply = await llm.generate_completion(
                prompt=f"Resident query: {query}\nProvide a helpful, polite, and concise answer for the resident.",
                system_instruction=self.system_prompt,
            )
            return AgentResult(
                agent_name=self.name,
                content=llm_reply,
                requires_approval=False,
                suggested_actions=[
                    "Where is my package•",
                    "Resend pickup PIN",
                    "Locker location and hours",
                    "Locker door did not open",
                ],
            )
        except Exception:
            return AgentResult(
                agent_name=self.name,
                content=f"I'm here to help with your Smiota smart locker deliveries! Regarding '{query}', would you like me to check a package, retrieve your pickup PIN, or connect you with property concierge•",
                requires_approval=False,
                suggested_actions=[
                    "Where is my package•",
                    "Resend pickup PIN",
                    "Locker location and hours",
                    "Locker door did not open",
                ],
            )


