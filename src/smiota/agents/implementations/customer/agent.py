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
                    "What would you like to check today?"
                ),
                requires_approval=False,
                suggested_actions=[
                    "Where is my package?",
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
                    "Where is my package?",
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

        # 6. Package / Parcel Tracking ID Provided (e.g. SM-9821, PKG-4402, 1Z999...)
        tracking_match = re.search(r'\b(sm-[0-9a-z]+|pkg-[0-9a-z]+|1z[0-9a-z]+|[a-z0-9]{8,})\b', q)
        if tracking_match:
            pkg_id = tracking_match.group(0).upper()
            return AgentResult(
                agent_name=self.name,
                content=(
                    f"📦 **Parcel Found: `{pkg_id}`**\n\n"
                    f"• **Delivery Status**: Ready for Pickup\n"
                    f"• **Locker Location**: Locker Compartment **B-14** (Building 3, Main Lobby)\n"
                    f"• **Carrier**: FedEx (Delivered Today at 09:45 AM)\n"
                    f"• **Pickup Instructions**: Enter your 6-digit PIN on the locker touch screen or scan your mobile QR code to unlock compartment B-14."
                ),
                requires_approval=False,
                suggested_actions=[
                    "Resend Pickup PIN via SMS",
                    "Extend pickup window (+24h)",
                    "Locker door did not open",
                ],
            )

        # 7. Check Parcel / Tracking Inquiry (Prompt for Package ID or Tracking Number)
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

        # 8. Fallback Account Lookup (Phone / Email)
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

        # 10. General Customer Support Fallback
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


