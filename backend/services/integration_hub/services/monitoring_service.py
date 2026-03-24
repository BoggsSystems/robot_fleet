"""
Monitoring Service - System Monitoring and Observability

This service handles:
- Performance metrics collection
- Distributed tracing
- Health monitoring
- Alert management
- Log aggregation
- Dashboard data
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
import uuid
import time
from collections import defaultdict, deque

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
import structlog

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for system monitoring and observability"""
    
    def __init__(self):
        """Initialize the monitoring service"""
        logger.info("Initializing Monitoring Service...")
        
        # Configuration
        self.config = {
            "metrics": {
                "collection_interval": 15,  # seconds
                "retention_period": 3600,    # 1 hour
                "export_prometheus": True
            },
            "tracing": {
                "sample_rate": 0.1,  # 10% sampling
                "export_jaeger": False,
                "export_zipkin": False
            },
            "alerts": {
                "enabled": True,
                "thresholds": {
                    "response_time": 1000,  # ms
                    "error_rate": 0.05,     # 5%
                    "cpu_usage": 0.8,       # 80%
                    "memory_usage": 0.85    # 85%
                }
            }
        }
        
        # Initialize metrics collection
        self.metrics_registry = CollectorRegistry()
        self._initialize_prometheus_metrics()
        
        # Initialize tracing
        self._initialize_tracing()
        
        # Data storage
        self.metrics_history = defaultdict(lambda: deque(maxlen=240))  # 1 hour at 15s intervals
        self.traces = deque(maxlen=1000)
        self.alerts = deque(maxlen=100)
        self.service_health = {}
        
        # Background tasks
        self.collection_running = False
        
        logger.info("Monitoring Service initialized")
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        
        # Service metrics
        self.request_counter = Counter(
            'warehouse_requests_total',
            'Total number of requests',
            ['service', 'method', 'endpoint', 'status'],
            registry=self.metrics_registry
        )
        
        self.request_duration = Histogram(
            'warehouse_request_duration_seconds',
            'Request duration in seconds',
            ['service', 'method', 'endpoint'],
            registry=self.metrics_registry
        )
        
        self.error_counter = Counter(
            'warehouse_errors_total',
            'Total number of errors',
            ['service', 'error_type'],
            registry=self.metrics_registry
        )
        
        self.active_connections = Gauge(
            'warehouse_active_connections',
            'Number of active connections',
            ['service'],
            registry=self.metrics_registry
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            'warehouse_cpu_usage_percent',
            'CPU usage percentage',
            ['service'],
            registry=self.metrics_registry
        )
        
        self.memory_usage = Gauge(
            'warehouse_memory_usage_percent',
            'Memory usage percentage',
            ['service'],
            registry=self.metrics_registry
        )
        
        # Business metrics
        self.mission_plans_generated = Counter(
            'warehouse_mission_plans_generated_total',
            'Total mission plans generated',
            registry=self.metrics_registry
        )
        
        self.robots_active = Gauge(
            'warehouse_robots_active',
            'Number of active robots',
            registry=self.metrics_registry
        )
        
        self.tasks_completed = Counter(
            'warehouse_tasks_completed_total',
            'Total tasks completed',
            ['task_type'],
            registry=self.metrics_registry
        )
    
    def _initialize_tracing(self):
        """Initialize distributed tracing"""
        try:
            # Set up tracing provider
            trace.set_tracer_provider(TracerProvider())
            tracer_provider = trace.get_tracer_provider()
            
            # Add span processor (would export to Jaeger/Zipkin in production)
            span_processor = BatchSpanProcessor(lambda x: None)  # Mock processor
            tracer_provider.add_span_processor(span_processor)
            
            # Set up metrics provider
            metric_reader = PrometheusMetricReader()
            meter_provider = MeterProvider(metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)
            
            self.tracer = trace.get_tracer(__name__)
            
        except Exception as e:
            logger.warning(f"Failed to initialize tracing: {e}")
            self.tracer = None
    
    async def start_metrics_collection(self):
        """Start background metrics collection"""
        if self.collection_running:
            return
        
        self.collection_running = True
        logger.info("Starting metrics collection")
        
        # Start collection task
        asyncio.create_task(self._collect_metrics_loop())
    
    async def _collect_metrics_loop(self):
        """Background loop for collecting metrics"""
        while self.collection_running:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect service metrics
                await self._collect_service_metrics()
                
                # Collect business metrics
                await self._collect_business_metrics()
                
                # Check for alerts
                await self._check_alerts()
                
                # Wait for next collection
                await asyncio.sleep(self.config["metrics"]["collection_interval"])
                
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        timestamp = datetime.utcnow().isoformat()
        
        # Mock system metrics (would use psutil or similar in production)
        system_metrics = {
            "cpu_usage": 0.45 + (time.time() % 100) / 200,  # Mock varying CPU
            "memory_usage": 0.62 + (time.time() % 100) / 300,  # Mock varying memory
            "disk_usage": 0.35,
            "network_io": {
                "bytes_sent": 1024000,
                "bytes_received": 2048000
            }
        }
        
        # Store in history
        self.metrics_history["system"].append({
            "timestamp": timestamp,
            "metrics": system_metrics
        })
        
        # Update Prometheus metrics
        self.cpu_usage.set(system_metrics["cpu_usage"], ["integration_hub"])
        self.memory_usage.set(system_metrics["memory_usage"], ["integration_hub"])
    
    async def _collect_service_metrics(self):
        """Collect service-specific metrics"""
        timestamp = datetime.utcnow().isoformat()
        
        services = ["digital_twin_service", "ai_engine", "integration_hub"]
        
        for service in services:
            try:
                # Mock service metrics (would collect from actual services)
                service_metrics = {
                    "request_count": int(100 + (time.time() % 50)),
                    "response_time": 150 + (time.time() % 200),  # ms
                    "error_rate": 0.02 + (time.time() % 100) / 1000,
                    "active_connections": 15 + int(time.time() % 10)
                }
                
                # Store in history
                self.metrics_history[service].append({
                    "timestamp": timestamp,
                    "metrics": service_metrics
                })
                
                # Update Prometheus metrics
                self.active_connections.set(
                    service_metrics["active_connections"], 
                    [service]
                )
                
                # Update service health
                self.service_health[service] = {
                    "status": "healthy" if service_metrics["error_rate"] < 0.05 else "degraded",
                    "last_check": timestamp,
                    "metrics": service_metrics
                }
                
            except Exception as e:
                logger.error(f"Failed to collect metrics for {service}: {str(e)}")
                self.service_health[service] = {
                    "status": "unhealthy",
                    "last_check": timestamp,
                    "error": str(e)
                }
    
    async def _collect_business_metrics(self):
        """Collect business-level metrics"""
        timestamp = datetime.utcnow().isoformat()
        
        # Mock business metrics
        business_metrics = {
            "robots_active": 8,
            "robots_idle": 2,
            "robots_charging": 2,
            "tasks_in_progress": 12,
            "tasks_completed_today": 145,
            "warehouse_throughput": 1250,  # items/hour
            "efficiency_score": 87.5
        }
        
        # Store in history
        self.metrics_history["business"].append({
            "timestamp": timestamp,
            "metrics": business_metrics
        })
        
        # Update Prometheus metrics
        self.robots_active.set(business_metrics["robots_active"])
    
    async def _check_alerts(self):
        """Check for alert conditions"""
        thresholds = self.config["alerts"]["thresholds"]
        
        for service, health_data in self.service_health.items():
            if "metrics" not in health_data:
                continue
            
            metrics = health_data["metrics"]
            
            # Check response time
            if metrics.get("response_time", 0) > thresholds["response_time"]:
                await self._create_alert(
                    "high_response_time",
                    service,
                    f"Response time {metrics['response_time']}ms exceeds threshold {thresholds['response_time']}ms",
                    "warning"
                )
            
            # Check error rate
            if metrics.get("error_rate", 0) > thresholds["error_rate"]:
                await self._create_alert(
                    "high_error_rate",
                    service,
                    f"Error rate {metrics['error_rate']:.2%} exceeds threshold {thresholds['error_rate']:.2%}",
                    "critical"
                )
        
        # Check system metrics
        if self.metrics_history["system"]:
            latest_system = self.metrics_history["system"][-1]["metrics"]
            
            if latest_system["cpu_usage"] > thresholds["cpu_usage"]:
                await self._create_alert(
                    "high_cpu_usage",
                    "system",
                    f"CPU usage {latest_system['cpu_usage']:.1%} exceeds threshold {thresholds['cpu_usage']:.1%}",
                    "warning"
                )
            
            if latest_system["memory_usage"] > thresholds["memory_usage"]:
                await self._create_alert(
                    "high_memory_usage",
                    "system",
                    f"Memory usage {latest_system['memory_usage']:.1%} exceeds threshold {thresholds['memory_usage']:.1%}",
                    "warning"
                )
    
    async def _create_alert(self, alert_type: str, service: str, message: str, severity: str):
        """Create and store alert"""
        alert = {
            "alert_id": str(uuid.uuid4()),
            "type": alert_type,
            "service": service,
            "message": message,
            "severity": severity,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        self.alerts.append(alert)
        logger.warning(f"Alert created: {alert_type} - {message}")
    
    async def record_request_sent(self, message: Dict):
        """Record message sent metric"""
        target_service = message.get("target_service", "unknown")
        message_type = message.get("message_type", "unknown")
        
        self.request_counter.labels(
            service="integration_hub",
            method="send",
            endpoint=f"message/{target_service}",
            status="sent"
        ).inc()
    
    async def record_request_forwarded(self, target_service: str, status_code: int):
        """Record request forwarded metric"""
        self.request_counter.labels(
            service="integration_hub",
            method="forward",
            endpoint=f"http/{target_service}",
            status=str(status_code)
        ).inc()
        
        # Record error if status code indicates error
        if status_code >= 400:
            self.error_counter.labels(
                service="integration_hub",
                error_type="http_error"
            ).inc()
    
    async def record_mission_plan_generated(self, mission_plan: Dict):
        """Record mission plan generation metric"""
        self.mission_plans_generated.inc()
        
        # Record duration if available
        if "generation_time" in mission_plan:
            self.request_duration.labels(
                service="ai_engine",
                method="post",
                endpoint="mission-plan"
            ).observe(mission_plan["generation_time"])
    
    async def get_service_metrics(self) -> Dict:
        """Get comprehensive service metrics"""
        return {
            "services": dict(self.service_health),
            "system": self._get_latest_metrics("system"),
            "business": self._get_latest_metrics("business"),
            "alerts": list(self.alerts)[-10:],  # Last 10 alerts
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_message_metrics(self) -> Dict:
        """Get message queue metrics"""
        # This would integrate with message queue service
        return {
            "messages_sent": 1250,
            "messages_received": 1180,
            "messages_failed": 15,
            "average_processing_time": 245,  # ms
            "queue_depth": {
                "digital_twin_service": 12,
                "ai_engine": 8
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        return {
            "response_time": {
                "avg": 185,
                "p50": 150,
                "p95": 450,
                "p99": 850
            },
            "throughput": {
                "requests_per_second": 45.2,
                "messages_per_second": 12.8
            },
            "error_rate": 0.023,
            "uptime": 99.85,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_latest_metrics(self, metric_type: str) -> Optional[Dict]:
        """Get latest metrics of a specific type"""
        if metric_type in self.metrics_history and self.metrics_history[metric_type]:
            return self.metrics_history[metric_type][-1]["metrics"]
        return None
    
    async def get_metrics_history(self, service: str, duration_minutes: int = 60) -> List[Dict]:
        """Get metrics history for a service"""
        if service not in self.metrics_history:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        
        history = []
        for entry in self.metrics_history[service]:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if entry_time >= cutoff_time:
                history.append(entry)
        
        return history
    
    async def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics export"""
        return generate_latest(self.metrics_registry).decode('utf-8')
    
    async def create_span(self, operation_name: str, **attributes) -> Any:
        """Create distributed tracing span"""
        if not self.tracer:
            return None
        
        try:
            span = self.tracer.start_span(operation_name)
            
            # Add attributes
            for key, value in attributes.items():
                span.set_attribute(key, value)
            
            return span
            
        except Exception as e:
            logger.error(f"Failed to create span: {str(e)}")
            return None
    
    async def get_trace_data(self, trace_id: str) -> Optional[Dict]:
        """Get trace data by ID"""
        # This would query trace storage (Jaeger, Zipkin, etc.)
        return None
    
    async def get_alerts(self, severity: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get alerts with optional filtering"""
        alerts = list(self.alerts)
        
        # Filter by severity
        if severity:
            alerts = [alert for alert in alerts if alert["severity"] == severity]
        
        # Sort by creation time (newest first)
        alerts.sort(key=lambda x: x["created_at"], reverse=True)
        
        return alerts[:limit]
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert["alert_id"] == alert_id:
                alert["status"] = "acknowledged"
                alert["acknowledged_at"] = datetime.utcnow().isoformat()
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        
        return False
    
    async def get_dashboard_data(self) -> Dict:
        """Get data for monitoring dashboard"""
        return {
            "overview": {
                "total_services": len(self.service_health),
                "healthy_services": len([s for s in self.service_health.values() if s.get("status") == "healthy"]),
                "active_alerts": len([a for a in self.alerts if a["status"] == "active"]),
                "total_requests": int(self.request_counter._value.sum() or 0)
            },
            "services": dict(self.service_health),
            "metrics": {
                "system": self._get_latest_metrics("system"),
                "business": self._get_latest_metrics("business")
            },
            "recent_alerts": list(self.alerts)[-5:],
            "performance": await self.get_performance_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def stop_metrics_collection(self):
        """Stop metrics collection"""
        self.collection_running = False
        logger.info("Metrics collection stopped")
    
    async def close(self):
        """Close monitoring service"""
        await self.stop_metrics_collection()
        logger.info("Monitoring Service closed")
