"""Asynchronous RabbitMQ Message Broker Service (aio-pika)."""
import json
from typing import Any, Callable, Coroutine, Optional
import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection, AbstractRobustChannel, AbstractExchange

from smiota.core.config import get_settings
from smiota.core.logging import logger

_connection: Optional[AbstractRobustConnection] = None
_channel: Optional[AbstractRobustChannel] = None
_exchange: Optional[AbstractExchange] = None


class RabbitMQService:
    """Asynchronous RabbitMQ service for topic publishing and subscription."""

    @classmethod
    async def get_connection(cls) -> AbstractRobustConnection:
        global _connection
        if _connection is None or _connection.is_closed:
            settings = get_settings()
            logger.info("Connecting to RabbitMQ broker...")
            _connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            logger.info("Connected to RabbitMQ successfully.")
        return _connection

    @classmethod
    async def get_channel(cls) -> AbstractRobustChannel:
        global _channel
        conn = await cls.get_connection()
        if _channel is None or _channel.is_closed:
            _channel = await conn.channel()
            await _channel.set_qos(prefetch_count=10)
        return _channel

    @classmethod
    async def get_exchange(cls) -> AbstractExchange:
        global _exchange
        channel = await cls.get_channel()
        if _exchange is None:
            settings = get_settings()
            _exchange = await channel.declare_exchange(
                name=settings.RABBITMQ_EXCHANGE,
                type=aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
        return _exchange

    @classmethod
    async def publish(cls, routing_key: str, message: dict[str, Any]) -> None:
        """Publish a JSON payload to the Smiota events topic exchange."""
        try:
            exchange = await cls.get_exchange()
            payload_bytes = json.dumps(message, default=str).encode("utf-8")
            msg = aio_pika.Message(
                body=payload_bytes,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await exchange.publish(msg, routing_key=routing_key)
            logger.info(f"Published event [{routing_key}] to RabbitMQ: {message.get('event_type', 'EVENT')}")
        except Exception as e:
            logger.error(f"Failed to publish to RabbitMQ: {e}", exc_info=True)
            raise

    @classmethod
    async def subscribe(
        cls,
        queue_name: str,
        routing_keys: list[str],
        callback: Callable[[dict[str, Any], str], Coroutine[Any, Any, None]],
    ) -> None:
        """Subscribe to specific topic routing keys and process incoming messages."""
        channel = await cls.get_channel()
        exchange = await cls.get_exchange()

        queue = await channel.declare_queue(queue_name, durable=True)
        for r_key in routing_keys:
            await queue.bind(exchange, routing_key=r_key)
            logger.info(f"Bound queue '{queue_name}' to routing key '{r_key}'")

        async def _on_message(msg: AbstractIncomingMessage):
            async with msg.process():
                try:
                    data = json.loads(msg.body.decode("utf-8"))
                    routing_key = msg.routing_key or ""
                    await callback(data, routing_key)
                except Exception as e:
                    logger.error(f"Error processing RabbitMQ message: {e}", exc_info=True)

        await queue.consume(_on_message)
        logger.info(f"Subscribed queue '{queue_name}' for consumption.")

    @classmethod
    async def close(cls) -> None:
        """Cleanly close connection."""
        global _connection, _channel, _exchange
        if _channel and not _channel.is_closed:
            await _channel.close()
            _channel = None
        if _connection and not _connection.is_closed:
            await _connection.close()
            _connection = None
        _exchange = None
        logger.info("RabbitMQ connection closed.")
