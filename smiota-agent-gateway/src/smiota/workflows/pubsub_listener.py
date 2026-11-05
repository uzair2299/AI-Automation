"""RabbitMQ Background Event Listener for Real-Time WebSocket Alerts."""
import asyncio
from typing import Any, Dict
from smiota.core.rabbitmq import RabbitMQService
from smiota.core.logging import logger
from smiota.api.v1.websocket_manager import ws_manager

_listener_task: asyncio.Task = None


async def handle_package_event(event: Dict[str, Any], routing_key: str) -> None:
    """Handle incoming package events from RabbitMQ and push to active WebSockets."""
    event_type = event.get("event_type", routing_key).upper()
    resident_id = event.get("resident_id") or event.get("resident", {}).get("resident_id")
    pkg_info = event.get("package", {})
    locker_info = event.get("locker", {})

    carrier = pkg_info.get("carrier", "Carrier")
    tracking = pkg_info.get("tracking_number", "N/A")
    compartment = pkg_info.get("compartment") or locker_info.get("compartment_number", "Locker")
    pin = pkg_info.get("pin") or locker_info.get("pickup_pin", "")

    pin_text = f" Pickup PIN: **{pin}**." if pin else ""
    body = f"A new delivery from **{carrier}** (`{tracking}`) is ready in **Compartment {compartment}**.{pin_text}"

    notification = {
        "type": "notification",
        "event_type": event_type,
        "title": "📦 Parcel Delivered!",
        "message": body,
        "data": event,
        "suggested_actions": [
            "Resend Pickup PIN",
            "Locker Location & Hours",
            "Door not opening / Help"
        ]
    }

    logger.info(f"Pushing real-time event [{event_type}] to WebSockets (Resident: {resident_id})...")

    delivered_count = 0
    if resident_id:
        delivered_count = await ws_manager.send_to_resident(str(resident_id), notification)

    # In single-tenant/staging mode or if resident wasn't mapped, broadcast to active tabs
    if delivered_count == 0 and len(ws_manager.active_sessions) > 0:
        delivered_count = await ws_manager.broadcast(notification)

    logger.info(f"Event [{event_type}] successfully delivered to {delivered_count} active WebSocket chat client(s).")


async def start_event_listener() -> None:
    """Start subscribing to RabbitMQ in the background."""
    logger.info("Initializing RabbitMQ background listener for 'package.*' events...")
    try:
        await RabbitMQService.subscribe(
            queue_name="smiota.ai.package.notifications",
            routing_keys=["package.*", "locker.*"],
            callback=handle_package_event,
        )
        logger.info("RabbitMQ real-time event listener is active and waiting for events.")
    except Exception as e:
        logger.warning(f"Could not connect RabbitMQ listener: {e}. Will retry when broker is available.")


def launch_listener_daemon() -> None:
    global _listener_task
    try:
        loop = asyncio.get_running_loop()
        _listener_task = loop.create_task(start_event_listener())
    except RuntimeError:
        pass
