"""
Message Queue Service - Centralized Message Management

This service handles:
- Azure Service Bus integration
- RabbitMQ support
- Redis pub/sub
- Message routing and filtering
- Priority queuing
- Dead letter handling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
import json
from datetime import datetime, timedelta
import uuid

from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.exceptions import ServiceBusException
import pika
import redis.asyncio as redis
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class MessageQueueService:
    """Service for managing message queues across different backends"""
    
    def __init__(self):
        """Initialize the message queue service"""
        logger.info("Initializing Message Queue Service...")
        
        # Configuration
        self.config = {
            "azure_service_bus": {
                "connection_string": "your-service-bus-connection-string",
                "enabled": True
            },
            "rabbitmq": {
                "host": "localhost",
                "port": 5672,
                "username": "guest",
                "password": "guest",
                "enabled": False
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "enabled": True
            }
        }
        
        # Initialize backends
        self.azure_client = None
        self.rabbitmq_connection = None
        self.redis_client = None
        
        # Message handlers
        self.message_handlers = {}
        self.consumer_tasks = {}
        
        # Message tracking
        self.message_status = {}
        self.dead_letter_queue = []
        
        # Initialize backends
        asyncio.create_task(self._initialize_backends())
        
        logger.info("Message Queue Service initialized")
    
    async def _initialize_backends(self):
        """Initialize all message queue backends"""
        # Initialize Azure Service Bus
        if self.config["azure_service_bus"]["enabled"]:
            try:
                self.azure_client = ServiceBusClient.from_connection_string(
                    self.config["azure_service_bus"]["connection_string"]
                )
                logger.info("Azure Service Bus initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Service Bus: {e}")
        
        # Initialize Redis
        if self.config["redis"]["enabled"]:
            try:
                self.redis_client = redis.Redis(
                    host=self.config["redis"]["host"],
                    port=self.config["redis"]["port"],
                    db=self.config["redis"]["db"],
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("Redis initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redis: {e}")
    
    async def send_message(self, message: Dict, backend: str = "auto") -> str:
        """
        Send message through appropriate queue backend
        
        Args:
            message: Message dictionary with required fields
            backend: Backend to use ("azure", "redis", "rabbitmq", "auto")
            
        Returns:
            Message ID
        """
        try:
            # Generate message ID if not provided
            message_id = message.get("message_id") or str(uuid.uuid4())
            message["message_id"] = message_id
            message["timestamp"] = datetime.utcnow().isoformat()
            
            # Track message status
            self.message_status[message_id] = {
                "status": "queued",
                "queued_at": datetime.utcnow().isoformat(),
                "backend": backend
            }
            
            # Choose backend
            selected_backend = self._choose_backend(backend)
            
            # Send message
            if selected_backend == "azure":
                await self._send_azure_service_bus(message)
            elif selected_backend == "redis":
                await self._send_redis(message)
            elif selected_backend == "rabbitmq":
                await self._send_rabbitmq(message)
            else:
                raise ValueError(f"Unsupported backend: {selected_backend}")
            
            logger.info(f"Message sent: {message_id} via {selected_backend}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            # Update message status
            if "message_id" in locals():
                self.message_status[message_id]["status"] = "failed"
                self.message_status[message_id]["error"] = str(e)
            raise
    
    def _choose_backend(self, backend: str) -> str:
        """Choose appropriate backend based on availability and preferences"""
        if backend == "auto":
            # Auto-select based on availability and message type
            if self.azure_client:
                return "azure"
            elif self.redis_client:
                return "redis"
            else:
                return "azure"  # Default fallback
        
        # Check if requested backend is available
        if backend == "azure" and self.azure_client:
            return "azure"
        elif backend == "redis" and self.redis_client:
            return "redis"
        elif backend == "rabbitmq" and self.rabbitmq_connection:
            return "rabbitmq"
        else:
            # Fallback to available backend
            if self.azure_client:
                return "azure"
            elif self.redis_client:
                return "redis"
            else:
                raise ValueError("No message queue backend available")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _send_azure_service_bus(self, message: Dict):
        """Send message via Azure Service Bus"""
        try:
            # Create queue name based on target service
            queue_name = f"warehouse-{message['target_service']}"
            
            # Create sender
            sender = self.azure_client.get_queue_sender(queue_name)
            
            # Create Service Bus message
            sb_message = ServiceBusMessage(
                body=json.dumps(message),
                message_id=message["message_id"],
                subject=message["message_type"],
                correlation_id=message.get("correlation_id"),
                application_properties={
                    "source_service": message["source_service"],
                    "priority": message.get("priority", "medium")
                }
            )
            
            # Send message
            await sender.send_messages(sb_message)
            await sender.close()
            
        except ServiceBusException as e:
            logger.error(f"Azure Service Bus error: {e}")
            raise
    
    async def _send_redis(self, message: Dict):
        """Send message via Redis pub/sub"""
        try:
            # Create channel name based on target service
            channel = f"warehouse:{message['target_service']}"
            
            # Publish message
            await self.redis_client.publish(
                channel,
                json.dumps(message)
            )
            
        except Exception as e:
            logger.error(f"Redis error: {e}")
            raise
    
    async def _send_rabbitmq(self, message: Dict):
        """Send message via RabbitMQ"""
        try:
            # Create connection if not exists
            if not self.rabbitmq_connection:
                self.rabbitmq_connection = await pika.connect_robust(
                    host=self.config["rabbitmq"]["host"],
                    port=self.config["rabbitmq"]["port"],
                    credentials=pika.PlainCredentials(
                        self.config["rabbitmq"]["username"],
                        self.config["rabbitmq"]["password"]
                    )
                )
            
            # Create channel
            channel = await self.rabbitmq_connection.channel()
            
            # Declare queue
            queue_name = f"warehouse-{message['target_service']}"
            await channel.queue_declare(queue=queue_name, durable=True)
            
            # Publish message
            await channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    message_id=message["message_id"],
                    correlation_id=message.get("correlation_id"),
                    priority=self._get_priority_value(message.get("priority", "medium")),
                    delivery_mode=2  # Persistent
                )
            )
            
            await channel.close()
            
        except Exception as e:
            logger.error(f"RabbitMQ error: {e}")
            raise
    
    def _get_priority_value(self, priority: str) -> int:
        """Convert priority string to numeric value"""
        priority_map = {
            "low": 1,
            "medium": 5,
            "high": 8,
            "critical": 10
        }
        return priority_map.get(priority, 5)
    
    async def start_consumers(self):
        """Start message consumers for all backends"""
        logger.info("Starting message consumers...")
        
        # Start Azure Service Bus consumers
        if self.azure_client:
            asyncio.create_task(self._start_azure_consumers())
        
        # Start Redis consumers
        if self.redis_client:
            asyncio.create_task(self._start_redis_consumers())
        
        # Start RabbitMQ consumers
        if self.rabbitmq_connection:
            asyncio.create_task(self._start_rabbitmq_consumers())
        
        logger.info("Message consumers started")
    
    async def _start_azure_consumers(self):
        """Start Azure Service Bus consumers"""
        try:
            # Define queues to consume from
            queues = ["warehouse-digital_twin_service", "warehouse-ai_engine"]
            
            for queue_name in queues:
                consumer_task = asyncio.create_task(
                    self._azure_consumer_loop(queue_name)
                )
                self.consumer_tasks[f"azure_{queue_name}"] = consumer_task
                
        except Exception as e:
            logger.error(f"Failed to start Azure consumers: {e}")
    
    async def _azure_consumer_loop(self, queue_name: str):
        """Azure Service Bus consumer loop"""
        while True:
            try:
                # Create receiver
                receiver = self.azure_client.get_queue_receiver(queue_name, max_wait_time=5)
                
                async for message in receiver:
                    try:
                        # Process message
                        message_data = json.loads(message.body)
                        await self._process_message(message_data, "azure")
                        
                        # Complete message
                        await receiver.complete_message(message)
                        
                    except Exception as e:
                        logger.error(f"Failed to process Azure message: {e}")
                        # Dead letter the message
                        await receiver.dead_letter_message(message)
                
                await receiver.close()
                
            except Exception as e:
                logger.error(f"Azure consumer error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _start_redis_consumers(self):
        """Start Redis consumers"""
        try:
            # Define channels to subscribe to
            channels = ["warehouse:digital_twin_service", "warehouse:ai_engine"]
            
            for channel in channels:
                consumer_task = asyncio.create_task(
                    self._redis_consumer_loop(channel)
                )
                self.consumer_tasks[f"redis_{channel}"] = consumer_task
                
        except Exception as e:
            logger.error(f"Failed to start Redis consumers: {e}")
    
    async def _redis_consumer_loop(self, channel: str):
        """Redis consumer loop"""
        try:
            # Subscribe to channel
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        # Process message
                        message_data = json.loads(message["data"])
                        await self._process_message(message_data, "redis")
                        
                    except Exception as e:
                        logger.error(f"Failed to process Redis message: {e}")
                        
        except Exception as e:
            logger.error(f"Redis consumer error: {e}")
            await asyncio.sleep(5)  # Wait before retrying
    
    async def _start_rabbitmq_consumers(self):
        """Start RabbitMQ consumers"""
        try:
            # Define queues to consume from
            queues = ["warehouse-digital_twin_service", "warehouse-ai_engine"]
            
            for queue_name in queues:
                consumer_task = asyncio.create_task(
                    self._rabbitmq_consumer_loop(queue_name)
                )
                self.consumer_tasks[f"rabbitmq_{queue_name}"] = consumer_task
                
        except Exception as e:
            logger.error(f"Failed to start RabbitMQ consumers: {e}")
    
    async def _rabbitmq_consumer_loop(self, queue_name: str):
        """RabbitMQ consumer loop"""
        while True:
            try:
                # Create connection and channel
                connection = await pika.connect_robust(
                    host=self.config["rabbitmq"]["host"],
                    port=self.config["rabbitmq"]["port"],
                    credentials=pika.PlainCredentials(
                        self.config["rabbitmq"]["username"],
                        self.config["rabbitmq"]["password"]
                    )
                )
                
                channel = await connection.channel()
                await channel.queue_declare(queue=queue_name, durable=True)
                
                # Set up consumer
                async def message_callback(channel, method, properties, body):
                    try:
                        # Process message
                        message_data = json.loads(body)
                        await self._process_message(message_data, "rabbitmq")
                        
                        # Acknowledge message
                        await channel.basic_ack(delivery_tag=method.delivery_tag)
                        
                    except Exception as e:
                        logger.error(f"Failed to process RabbitMQ message: {e}")
                        # Negative acknowledge (requeue)
                        await channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
                await channel.basic_consume(queue=queue_name, on_message_callback=message_callback)
                
                # Start consuming
                await channel.start_consuming()
                
            except Exception as e:
                logger.error(f"RabbitMQ consumer error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_message(self, message: Dict, backend: str):
        """Process received message"""
        try:
            message_id = message["message_id"]
            
            # Update message status
            if message_id in self.message_status:
                self.message_status[message_id]["status"] = "processing"
                self.message_status[message_id]["processed_at"] = datetime.utcnow().isoformat()
                self.message_status[message_id]["backend"] = backend
            
            # Get message handler
            target_service = message["target_service"]
            handler = self.message_handlers.get(target_service)
            
            if handler:
                # Call handler
                await handler(message)
                
                # Update status
                if message_id in self.message_status:
                    self.message_status[message_id]["status"] = "completed"
                    self.message_status[message_id]["completed_at"] = datetime.utcnow().isoformat()
            else:
                # No handler found
                logger.warning(f"No handler for service: {target_service}")
                if message_id in self.message_status:
                    self.message_status[message_id]["status"] = "no_handler"
                    self.message_status[message_id]["error"] = f"No handler for {target_service}"
            
            logger.info(f"Message processed: {message_id}")
            
        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            # Update status
            if "message_id" in locals():
                self.message_status[message_id]["status"] = "failed"
                self.message_status[message_id]["error"] = str(e)
    
    def register_handler(self, service_name: str, handler: Callable):
        """Register message handler for a service"""
        self.message_handlers[service_name] = handler
        logger.info(f"Handler registered for service: {service_name}")
    
    async def get_message_status(self, message_id: str) -> Dict:
        """Get message processing status"""
        if message_id not in self.message_status:
            return {"error": "Message not found"}
        
        return self.message_status[message_id]
    
    async def health_check(self) -> str:
        """Check health of message queue service"""
        try:
            # Check Azure Service Bus
            azure_healthy = True
            if self.azure_client:
                try:
                    # Try to create a test sender
                    sender = self.azure_client.get_queue_sender("test")
                    await sender.close()
                except Exception:
                    azure_healthy = False
            
            # Check Redis
            redis_healthy = True
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                except Exception:
                    redis_healthy = False
            
            # Check RabbitMQ
            rabbitmq_healthy = True
            if self.rabbitmq_connection:
                try:
                    # Check connection status
                    if self.rabbitmq_connection.is_closed:
                        rabbitmq_healthy = False
                except Exception:
                    rabbitmq_healthy = False
            
            # Overall health
            if azure_healthy or redis_healthy or rabbitmq_healthy:
                return "healthy"
            else:
                return "unhealthy"
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return "unhealthy"
    
    async def get_queue_metrics(self) -> Dict:
        """Get queue metrics"""
        metrics = {
            "total_messages": len(self.message_status),
            "message_status_breakdown": {},
            "backend_health": {},
            "dead_letter_count": len(self.dead_letter_queue)
        }
        
        # Count messages by status
        status_counts = {}
        for status_info in self.message_status.values():
            status = status_info["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        metrics["message_status_breakdown"] = status_counts
        
        # Backend health
        metrics["backend_health"] = {
            "azure": "healthy" if self.azure_client else "disabled",
            "redis": "healthy" if self.redis_client else "disabled",
            "rabbitmq": "healthy" if self.rabbitmq_connection else "disabled"
        }
        
        return metrics
