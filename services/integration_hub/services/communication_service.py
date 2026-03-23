"""
Communication Service - HTTP Communication Between Services

This service handles:
- HTTP request forwarding
- Service discovery
- Load balancing
- Timeout management
- Retry mechanisms
- Response transformation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
import uuid

import httpx
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from circuitbreaker import circuit, CircuitBreakerError

logger = logging.getLogger(__name__)


class CommunicationService:
    """Service for HTTP communication between services"""
    
    def __init__(self):
        """Initialize the communication service"""
        logger.info("Initializing Communication Service...")
        
        # Service registry
        self.service_registry = {
            "digital_twin_service": {
                "url": "http://localhost:7000",
                "health_endpoint": "/health",
                "timeout": 30,
                "retry_attempts": 3
            },
            "ai_engine": {
                "url": "http://localhost:8000",
                "health_endpoint": "/health",
                "timeout": 30,
                "retry_attempts": 3
            },
            "integration_hub": {
                "url": "http://localhost:9000",
                "health_endpoint": "/health",
                "timeout": 30,
                "retry_attempts": 3
            }
        }
        
        # HTTP clients
        self.httpx_client = httpx.AsyncClient(timeout=30.0)
        self.aiohttp_session = None
        
        # Circuit breakers
        self.circuit_breakers = {}
        self._initialize_circuit_breakers()
        
        # Request tracking
        self.request_history = {}
        self.response_cache = {}
        
        logger.info("Communication Service initialized")
    
    def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for all services"""
        for service_name in self.service_registry.keys():
            self.circuit_breakers[service_name] = circuit(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=Exception
            )(self._make_request_with_circuit_breaker)
    
    async def forward_request(
        self,
        target_service: str,
        endpoint: str,
        payload: Dict,
        method: str = "POST",
        timeout: Optional[int] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """
        Forward HTTP request to target service
        
        Args:
            target_service: Name of target service
            endpoint: API endpoint
            payload: Request payload
            method: HTTP method
            timeout: Request timeout
            headers: Additional headers
            
        Returns:
            Response data
        """
        try:
            logger.info(f"Forwarding {method} request to {target_service}: {endpoint}")
            
            # Get service configuration
            service_config = self.service_registry.get(target_service)
            if not service_config:
                raise ValueError(f"Unknown service: {target_service}")
            
            # Build full URL
            full_url = f"{service_config['url']}{endpoint}"
            
            # Set timeout
            request_timeout = timeout or service_config["timeout"]
            
            # Generate request ID
            request_id = str(uuid.uuid4())
            
            # Track request
            self.request_history[request_id] = {
                "target_service": target_service,
                "endpoint": endpoint,
                "method": method,
                "started_at": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            try:
                # Make request with circuit breaker
                response = await self.circuit_breakers[target_service](
                    method=method,
                    url=full_url,
                    payload=payload,
                    timeout=request_timeout,
                    headers=headers
                )
                
                # Update request tracking
                self.request_history[request_id]["status"] = "completed"
                self.request_history[request_id]["completed_at"] = datetime.utcnow().isoformat()
                self.request_history[request_id]["response_status"] = response.get("status_code", 200)
                
                logger.info(f"Request completed: {request_id}")
                return response
                
            except CircuitBreakerError as e:
                # Circuit breaker is open
                self.request_history[request_id]["status"] = "circuit_breaker_open"
                self.request_history[request_id]["error"] = str(e)
                
                logger.warning(f"Circuit breaker open for {target_service}")
                return {
                    "status_code": 503,
                    "error": "Service temporarily unavailable",
                    "circuit_breaker": "open",
                    "request_id": request_id
                }
            
        except Exception as e:
            logger.error(f"Failed to forward request: {str(e)}")
            
            # Update request tracking
            if "request_id" in locals():
                self.request_history[request_id]["status"] = "failed"
                self.request_history[request_id]["error"] = str(e)
            
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _make_request_with_circuit_breaker(
        self,
        method: str,
        url: str,
        payload: Dict,
        timeout: int,
        headers: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request with retry logic"""
        
        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "WarehouseIntegrationHub/1.0",
            "X-Request-ID": str(uuid.uuid4()),
            "X-Timestamp": datetime.utcnow().isoformat()
        }
        
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = await self.httpx_client.get(
                    url,
                    headers=request_headers,
                    timeout=timeout
                )
            elif method.upper() == "POST":
                response = await self.httpx_client.post(
                    url,
                    json=payload,
                    headers=request_headers,
                    timeout=timeout
                )
            elif method.upper() == "PUT":
                response = await self.httpx_client.put(
                    url,
                    json=payload,
                    headers=request_headers,
                    timeout=timeout
                )
            elif method.upper() == "DELETE":
                response = await self.httpx_client.delete(
                    url,
                    headers=request_headers,
                    timeout=timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check response status
            response.raise_for_status()
            
            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"content": response.text}
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
                "response_time": response.elapsed.total_seconds() if response.elapsed else 0
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "status_code": e.response.status_code,
                "error": str(e),
                "response_text": e.response.text
            }
        except httpx.TimeoutException:
            logger.error(f"Request timeout: {url}")
            raise Exception(f"Request timeout after {timeout} seconds")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    async def make_request(
        self,
        method: str,
        url: str,
        payload: Optional[Dict] = None,
        timeout: int = 30,
        headers: Optional[Dict] = None
    ) -> Dict:
        """Make direct HTTP request (for health checks, etc.)"""
        try:
            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "WarehouseIntegrationHub/1.0"
            }
            
            if headers:
                request_headers.update(headers)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=request_headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=payload, headers=request_headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                return {
                    "status": response.status_code,
                    "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
                
        except Exception as e:
            logger.error(f"Direct request failed: {str(e)}")
            return {"status": 500, "error": str(e)}
    
    async def broadcast_message(
        self,
        message: Dict,
        target_services: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Broadcast message to multiple services
        
        Args:
            message: Message to broadcast
            target_services: List of target services (all if None)
            
        Returns:
            Dictionary of service responses
        """
        try:
            logger.info(f"Broadcasting message to services: {target_services or 'all'}")
            
            # Determine target services
            if target_services is None:
                target_services = list(self.service_registry.keys())
            
            # Send to all services concurrently
            tasks = []
            for service in target_services:
                task = asyncio.create_task(
                    self.forward_request(
                        target_service=service,
                        endpoint="/api/messages/receive",
                        payload=message,
                        method="POST"
                    )
                )
                tasks.append((service, task))
            
            # Wait for all responses
            responses = {}
            for service, task in tasks:
                try:
                    response = await task
                    responses[service] = response
                except Exception as e:
                    responses[service] = {
                        "status_code": 500,
                        "error": str(e)
                    }
            
            return responses
            
        except Exception as e:
            logger.error(f"Broadcast failed: {str(e)}")
            raise
    
    async def check_service_health(self, service_name: str) -> Dict:
        """Check health of specific service"""
        try:
            service_config = self.service_registry.get(service_name)
            if not service_config:
                return {"status": "unknown", "error": "Service not found"}
            
            health_url = f"{service_config['url']}{service_config['health_endpoint']}"
            
            response = await self.make_request("GET", health_url, timeout=5)
            
            return {
                "service": service_name,
                "status": "healthy" if response["status"] == 200 else "unhealthy",
                "response": response,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "service": service_name,
                "status": "unhealthy",
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def check_all_services_health(self) -> Dict[str, Dict]:
        """Check health of all registered services"""
        logger.info("Checking health of all services")
        
        # Check all services concurrently
        tasks = []
        for service_name in self.service_registry.keys():
            task = asyncio.create_task(self.check_service_health(service_name))
            tasks.append((service_name, task))
        
        # Collect results
        health_results = {}
        for service_name, task in tasks:
            try:
                health_results[service_name] = await task
            except Exception as e:
                health_results[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_results
    
    async def get_service_metrics(self, service_name: str) -> Dict:
        """Get metrics for specific service"""
        try:
            service_config = self.service_registry.get(service_name)
            if not service_config:
                return {"error": "Service not found"}
            
            # Get service metrics
            metrics_url = f"{service_config['url']}/api/metrics"
            
            response = await self.make_request("GET", metrics_url)
            
            return {
                "service": service_name,
                "metrics": response.get("data", {}),
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "service": service_name,
                "error": str(e),
                "retrieved_at": datetime.utcnow().isoformat()
            }
    
    def register_service(self, service_name: str, config: Dict):
        """Register new service"""
        self.service_registry[service_name] = config
        
        # Create circuit breaker for new service
        self.circuit_breakers[service_name] = circuit(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )(self._make_request_with_circuit_breaker)
        
        logger.info(f"Service registered: {service_name}")
    
    def unregister_service(self, service_name: str):
        """Unregister service"""
        if service_name in self.service_registry:
            del self.service_registry[service_name]
        
        if service_name in self.circuit_breakers:
            del self.circuit_breakers[service_name]
        
        logger.info(f"Service unregistered: {service_name}")
    
    async def get_request_history(self, limit: int = 100) -> List[Dict]:
        """Get recent request history"""
        # Sort by timestamp and limit
        sorted_requests = sorted(
            self.request_history.values(),
            key=lambda x: x.get("started_at", ""),
            reverse=True
        )
        
        return sorted_requests[:limit]
    
    async def clear_request_history(self):
        """Clear request history"""
        self.request_history.clear()
        logger.info("Request history cleared")
    
    async def get_circuit_breaker_status(self) -> Dict[str, Dict]:
        """Get circuit breaker status for all services"""
        status = {}
        
        for service_name, breaker in self.circuit_breakers.items():
            status[service_name] = {
                "state": breaker.state,
                "failure_count": breaker.failure_count,
                "success_count": breaker.success_count,
                "last_failure_time": breaker.last_failure_time
            }
        
        return status
    
    async def reset_circuit_breaker(self, service_name: str):
        """Reset circuit breaker for specific service"""
        if service_name in self.circuit_breakers:
            breaker = self.circuit_breakers[service_name]
            breaker.state = "closed"
            breaker.failure_count = 0
            breaker.success_count = 0
            
            logger.info(f"Circuit breaker reset for: {service_name}")
    
    async def close(self):
        """Close communication service"""
        await self.httpx_client.aclose()
        
        if self.aiohttp_session:
            await self.aiohttp_session.close()
        
        logger.info("Communication Service closed")
