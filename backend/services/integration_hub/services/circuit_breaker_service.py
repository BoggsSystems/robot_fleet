"""
Circuit Breaker Service - Fault Tolerance and Resilience

This service handles:
- Circuit breaker patterns
- Service health monitoring
- Automatic failover
- Recovery mechanisms
- Load shedding
- Service degradation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
import time
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, blocking calls
    HALF_OPEN = "half_open"  # Testing if service has recovered


class ServiceHealth(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: int = 60          # Seconds to wait before trying again
    success_threshold: int = 3          # Successes needed to close circuit
    timeout: int = 30                  # Request timeout in seconds
    monitoring_period: int = 300       # Period to evaluate health (seconds)
    degradation_threshold: float = 0.2  # Performance degradation threshold


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None


class CircuitBreakerService:
    """Service for circuit breaker management and fault tolerance"""
    
    def __init__(self):
        """Initialize the circuit breaker service"""
        logger.info("Initializing Circuit Breaker Service...")
        
        # Circuit breaker storage
        self.circuits = {}
        self.service_configs = {}
        
        # Service health monitoring
        self.service_health = {}
        self.service_metrics = defaultdict(ServiceMetrics)
        
        # Background monitoring task
        self.monitoring_task = None
        self.monitoring_running = False
        
        # Default configuration
        self.default_config = CircuitBreakerConfig()
        
        # Initialize default circuits
        self._initialize_default_circuits()
        
        logger.info("Circuit Breaker Service initialized")
    
    def _initialize_default_circuits(self):
        """Initialize circuit breakers for default services"""
        default_services = [
            "digital_twin_service",
            "ai_engine",
            "integration_hub",
            "message_queue",
            "database"
        ]
        
        for service in default_services:
            self.register_service(service, self.default_config)
    
    def register_service(self, service_name: str, config: CircuitBreakerConfig):
        """Register a service with circuit breaker"""
        self.circuits[service_name] = {
            "state": CircuitState.CLOSED,
            "failure_count": 0,
            "success_count": 0,
            "last_failure_time": None,
            "last_state_change": datetime.utcnow(),
            "config": config
        }
        
        self.service_configs[service_name] = config
        self.service_health[service_name] = ServiceHealth.UNKNOWN
        
        logger.info(f"Circuit breaker registered for service: {service_name}")
    
    def unregister_service(self, service_name: str):
        """Unregister a service"""
        if service_name in self.circuits:
            del self.circuits[service_name]
        
        if service_name in self.service_configs:
            del self.service_configs[service_name]
        
        if service_name in self.service_health:
            del self.service_health[service_name]
        
        if service_name in self.service_metrics:
            del self.service_metrics[service_name]
        
        logger.info(f"Circuit breaker unregistered for service: {service_name}")
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if service is available through circuit breaker"""
        circuit = self.circuits.get(service_name)
        
        if not circuit:
            # Service not registered, assume available
            return True
        
        state = circuit["state"]
        
        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._should_attempt_reset(circuit):
                circuit["state"] = CircuitState.HALF_OPEN
                circuit["success_count"] = 0
                logger.info(f"Circuit breaker half-open for service: {service_name}")
                return True
            return False
        elif state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def _should_attempt_reset(self, circuit: Dict) -> bool:
        """Check if circuit should attempt reset"""
        if not circuit["last_failure_time"]:
            return True
        
        time_since_failure = datetime.utcnow() - circuit["last_failure_time"]
        return time_since_failure.total_seconds() >= circuit["config"].recovery_timeout
    
    async def call_service(self, service_name: str, operation_func, *args, **kwargs):
        """
        Call service through circuit breaker
        
        Args:
            service_name: Name of the service
            operation_func: Function to call
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            Exception: If circuit is open or call fails
        """
        circuit = self.circuits.get(service_name)
        
        if not circuit:
            # No circuit breaker, call directly
            return await self._execute_call(service_name, operation_func, *args, **kwargs)
        
        if not self.is_service_available(service_name):
            raise Exception(f"Circuit breaker open for service: {service_name}")
        
        try:
            start_time = time.time()
            result = await self._execute_call(service_name, operation_func, *args, **kwargs)
            response_time = time.time() - start_time
            
            # Record success
            self._record_success(service_name, response_time)
            
            # Check if circuit should close
            if circuit["state"] == CircuitState.HALF_OPEN:
                circuit["success_count"] += 1
                if circuit["success_count"] >= circuit["config"].success_threshold:
                    self._close_circuit(service_name)
            
            return result
            
        except Exception as e:
            # Record failure
            self._record_failure(service_name, str(e))
            
            # Check if circuit should open
            if circuit["state"] == CircuitState.CLOSED:
                circuit["failure_count"] += 1
                if circuit["failure_count"] >= circuit["config"].failure_threshold:
                    self._open_circuit(service_name)
            elif circuit["state"] == CircuitState.HALF_OPEN:
                self._open_circuit(service_name)
            
            raise
    
    async def _execute_call(self, service_name: str, operation_func, *args, **kwargs):
        """Execute the actual service call with timeout"""
        circuit = self.circuits.get(service_name)
        timeout = circuit["config"].timeout if circuit else self.default_config.timeout
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(operation_func(*args, **kwargs), timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            raise Exception(f"Service call timeout after {timeout} seconds")
    
    def _record_success(self, service_name: str, response_time: float):
        """Record successful call"""
        metrics = self.service_metrics[service_name]
        
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.last_success_time = datetime.utcnow()
        metrics.last_request_time = datetime.utcnow()
        
        # Update average response time
        if metrics.total_requests == 1:
            metrics.average_response_time = response_time
        else:
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_requests - 1) + response_time) /
                metrics.total_requests
            )
        
        # Update service health
        self._update_service_health(service_name)
    
    def _record_failure(self, service_name: str, error: str):
        """Record failed call"""
        circuit = self.circuits.get(service_name)
        metrics = self.service_metrics[service_name]
        
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.last_failure_time = datetime.utcnow()
        metrics.last_request_time = datetime.utcnow()
        
        if circuit:
            circuit["last_failure_time"] = datetime.utcnow()
        
        # Update service health
        self._update_service_health(service_name)
    
    def _update_service_health(self, service_name: str):
        """Update service health based on metrics"""
        metrics = self.service_metrics[service_name]
        
        if metrics.total_requests == 0:
            self.service_health[service_name] = ServiceHealth.UNKNOWN
            return
        
        # Calculate success rate
        success_rate = metrics.successful_requests / metrics.total_requests
        
        # Calculate recent performance (last 10 requests)
        recent_performance = self._calculate_recent_performance(service_name)
        
        # Determine health
        if success_rate >= 0.95 and recent_performance >= 0.9:
            self.service_health[service_name] = ServiceHealth.HEALTHY
        elif success_rate >= 0.8 and recent_performance >= 0.7:
            self.service_health[service_name] = ServiceHealth.DEGRADED
        else:
            self.service_health[service_name] = ServiceHealth.UNHEALTHY
    
    def _calculate_recent_performance(self, service_name: str) -> float:
        """Calculate recent performance score"""
        metrics = self.service_metrics[service_name]
        
        if metrics.total_requests < 5:
            return 1.0  # Not enough data, assume good
        
        # Factors: success rate, response time consistency
        success_rate = metrics.successful_requests / metrics.total_requests
        
        # Response time score (lower is better, normalize to 0-1)
        response_time_score = max(0, 1 - (metrics.average_response_time / 1000))  # 1s as baseline
        
        # Combine scores
        performance = (success_rate * 0.7) + (response_time_score * 0.3)
        
        return performance
    
    def _open_circuit(self, service_name: str):
        """Open circuit breaker"""
        circuit = self.circuits[service_name]
        circuit["state"] = CircuitState.OPEN
        circuit["last_state_change"] = datetime.utcnow()
        
        logger.warning(f"Circuit breaker opened for service: {service_name}")
    
    def _close_circuit(self, service_name: str):
        """Close circuit breaker"""
        circuit = self.circuits[service_name]
        circuit["state"] = CircuitState.CLOSED
        circuit["failure_count"] = 0
        circuit["success_count"] = 0
        circuit["last_state_change"] = datetime.utcnow()
        
        logger.info(f"Circuit breaker closed for service: {service_name}")
    
    def get_circuit_status(self, service_name: str) -> Dict:
        """Get circuit breaker status for a service"""
        circuit = self.circuits.get(service_name)
        
        if not circuit:
            return {"error": "Service not found"}
        
        metrics = self.service_metrics[service_name]
        health = self.service_health.get(service_name, ServiceHealth.UNKNOWN)
        
        return {
            "service": service_name,
            "state": circuit["state"].value,
            "failure_count": circuit["failure_count"],
            "success_count": circuit["success_count"],
            "last_failure_time": circuit["last_failure_time"].isoformat() if circuit["last_failure_time"] else None,
            "last_state_change": circuit["last_state_change"].isoformat(),
            "health": health.value,
            "metrics": {
                "total_requests": metrics.total_requests,
                "success_rate": metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0,
                "average_response_time": metrics.average_response_time,
                "last_success_time": metrics.last_success_time.isoformat() if metrics.last_success_time else None,
                "last_failure_time": metrics.last_failure_time.isoformat() if metrics.last_failure_time else None
            },
            "config": {
                "failure_threshold": circuit["config"].failure_threshold,
                "recovery_timeout": circuit["config"].recovery_timeout,
                "success_threshold": circuit["config"].success_threshold,
                "timeout": circuit["config"].timeout
            }
        }
    
    async def get_all_circuit_status(self) -> Dict[str, Dict]:
        """Get circuit breaker status for all services"""
        status = {}
        
        for service_name in self.circuits.keys():
            status[service_name] = self.get_circuit_status(service_name)
        
        return status
    
    def reset_circuit(self, service_name: str) -> bool:
        """Manually reset circuit breaker"""
        circuit = self.circuits.get(service_name)
        
        if not circuit:
            return False
        
        self._close_circuit(service_name)
        logger.info(f"Circuit breaker manually reset for service: {service_name}")
        return True
    
    def force_open_circuit(self, service_name: str) -> bool:
        """Manually force circuit breaker open"""
        circuit = self.circuits.get(service_name)
        
        if not circuit:
            return False
        
        circuit["state"] = CircuitState.OPEN
        circuit["last_state_change"] = datetime.utcnow()
        
        logger.warning(f"Circuit breaker manually forced open for service: {service_name}")
        return True
    
    async def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring_running:
            return
        
        self.monitoring_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Circuit breaker monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Circuit breaker monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_running:
            try:
                await self._monitor_service_health()
                await self._check_service_degradation()
                await self._cleanup_old_data()
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _monitor_service_health(self):
        """Monitor overall service health"""
        for service_name in self.circuits.keys():
            health = self.service_health.get(service_name, ServiceHealth.UNKNOWN)
            
            # Log health changes
            if health == ServiceHealth.UNHEALTHY:
                logger.warning(f"Service unhealthy: {service_name}")
            elif health == ServiceHealth.DEGRADED:
                logger.info(f"Service degraded: {service_name}")
    
    async def _check_service_degradation(self):
        """Check for service performance degradation"""
        for service_name, config in self.service_configs.items():
            metrics = self.service_metrics[service_name]
            
            if metrics.total_requests < 10:
                continue  # Not enough data
            
            # Check performance degradation
            recent_performance = self._calculate_recent_performance(service_name)
            
            if recent_performance < (1.0 - config.degradation_threshold):
                logger.warning(f"Service performance degradation detected: {service_name} (performance: {recent_performance:.2f})")
                
                # Consider opening circuit if severely degraded
                if recent_performance < 0.5:
                    circuit = self.circuits.get(service_name)
                    if circuit and circuit["state"] == CircuitState.CLOSED:
                        logger.warning(f"Opening circuit due to severe degradation: {service_name}")
                        self._open_circuit(service_name)
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # This would clean up old metrics data
        # For now, just log the cleanup
        logger.debug("Performing monitoring data cleanup")
    
    def get_service_health_summary(self) -> Dict:
        """Get summary of all service health"""
        health_counts = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "unknown": 0
        }
        
        for health in self.service_health.values():
            health_counts[health.value] += 1
        
        return {
            "total_services": len(self.service_health),
            "health_breakdown": health_counts,
            "overall_health": "healthy" if health_counts["unhealthy"] == 0 else "degraded" if health_counts["unhealthy"] < len(self.service_health) / 2 else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_load_shedding_recommendations(self) -> List[Dict]:
        """Get load shedding recommendations for degraded services"""
        recommendations = []
        
        for service_name, health in self.service_health.items():
            if health == ServiceHealth.UNHEALTHY:
                circuit = self.circuits.get(service_name)
                metrics = self.service_metrics[service_name]
                
                recommendation = {
                    "service": service_name,
                    "action": "load_shed",
                    "reason": "Service unhealthy",
                    "priority": "high",
                    "metrics": {
                        "success_rate": metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0,
                        "average_response_time": metrics.average_response_time
                    },
                    "suggested_actions": [
                        "Enable circuit breaker",
                        "Reduce request rate",
                        "Enable fallback responses"
                    ]
                }
                
                recommendations.append(recommendation)
            
            elif health == ServiceHealth.DEGRADED:
                circuit = self.circuits.get(service_name)
                metrics = self.service_metrics[service_name]
                
                recommendation = {
                    "service": service_name,
                    "action": "monitor",
                    "reason": "Service degraded",
                    "priority": "medium",
                    "metrics": {
                        "success_rate": metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0,
                        "average_response_time": metrics.average_response_time
                    },
                    "suggested_actions": [
                        "Monitor closely",
                        "Prepare fallback options",
                        "Consider rate limiting"
                    ]
                }
                
                recommendations.append(recommendation)
        
        return recommendations
