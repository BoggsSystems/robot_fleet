"""
Analytics Service - Advanced Analytics and Predictions for Warehouse Operations

This service handles:
- Predictive analytics
- Performance metrics
- Trend analysis
- Anomaly detection
"""

import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
import uuid
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for advanced analytics and predictions"""
    
    def __init__(self):
        """Initialize the analytics service"""
        logger.info("Initializing Analytics Service...")
        
        # Initialize ML models
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
        # Initialize data storage
        self.historical_data = []
        self.performance_metrics = {}
        
        # Initialize with sample data
        self._initialize_sample_data()
        
        logger.info("Analytics Service initialized successfully")
    
    async def generate_prediction(self, prediction_type: str, parameters: Dict = None, time_horizon: str = "24h") -> Dict:
        """
        Generate predictions using various ML models
        
        Args:
            prediction_type: Type of prediction (maintenance, performance, inventory, etc.)
            parameters: Additional parameters for prediction
            time_horizon: Time horizon for prediction
            
        Returns:
            Prediction result with confidence scores
        """
        try:
            logger.info(f"Generating {prediction_type} prediction for {time_horizon}")
            
            parameters = parameters or {}
            
            if prediction_type == "maintenance":
                return await self._predict_maintenance(parameters, time_horizon)
            elif prediction_type == "performance":
                return await self._predict_performance(parameters, time_horizon)
            elif prediction_type == "inventory":
                return await self._predict_inventory(parameters, time_horizon)
            elif prediction_type == "throughput":
                return await self._predict_throughput(parameters, time_horizon)
            elif prediction_type == "anomaly":
                return await self._detect_anomalies(parameters)
            else:
                raise ValueError(f"Unsupported prediction type: {prediction_type}")
                
        except Exception as e:
            logger.error(f"Failed to generate prediction: {str(e)}")
            raise
    
    async def get_performance_metrics(self) -> Dict:
        """
        Get current warehouse performance metrics
        
        Returns:
            Dictionary of performance metrics
        """
        try:
            logger.info("Getting performance metrics")
            
            # Calculate real-time metrics
            metrics = {
                "throughput": self._calculate_throughput(),
                "efficiency": self._calculate_efficiency(),
                "error_rate": self._calculate_error_rate(),
                "uptime": self._calculate_uptime(),
                "robot_utilization": self._calculate_robot_utilization(),
                "zone_utilization": self._calculate_zone_utilization(),
                "average_task_duration": self._calculate_average_task_duration(),
                "battery_efficiency": self._calculate_battery_efficiency(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store for historical analysis
            self.performance_metrics = metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            raise
    
    async def get_trend_analysis(self, metric: str, period: str = "7d") -> Dict:
        """
        Get trend analysis for a specific metric
        
        Args:
            metric: Metric to analyze
            period: Time period for analysis
            
        Returns:
            Trend analysis results
        """
        try:
            logger.info(f"Getting trend analysis for {metric} over {period}")
            
            # Get historical data for the metric
            historical_values = self._get_historical_values(metric, period)
            
            if not historical_values:
                return {"error": "No historical data available"}
            
            # Calculate trend statistics
            values = [v["value"] for v in historical_values]
            timestamps = [v["timestamp"] for v in historical_values]
            
            trend_analysis = {
                "metric": metric,
                "period": period,
                "data_points": len(values),
                "current_value": values[-1] if values else 0,
                "average": np.mean(values),
                "median": np.median(values),
                "min": np.min(values),
                "max": np.max(values),
                "std_dev": np.std(values),
                "trend": self._calculate_trend(values),
                "change_percentage": self._calculate_change_percentage(values),
                "forecast": self._simple_forecast(values, 5),  # 5-point forecast
                "anomalies": self._detect_anomalies_in_values(values),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Failed to get trend analysis: {str(e)}")
            raise
    
    async def _predict_maintenance(self, parameters: Dict, time_horizon: str) -> Dict:
        """Predict maintenance needs"""
        
        # Mock maintenance prediction
        robot_id = parameters.get("robot_id", "robot-001")
        hours = int(time_horizon.replace("h", "")) if "h" in time_horizon else 24
        
        # Simulate prediction based on historical patterns
        maintenance_probability = np.random.uniform(0.1, 0.8)
        
        prediction = {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "maintenance",
            "target": robot_id,
            "time_horizon": time_horizon,
            "results": {
                "maintenance_probability": maintenance_probability,
                "predicted_failure_time": (datetime.utcnow() + timedelta(hours=hours * maintenance_probability)).isoformat(),
                "risk_level": "high" if maintenance_probability > 0.7 else "medium" if maintenance_probability > 0.4 else "low",
                "recommended_actions": self._get_maintenance_recommendations(maintenance_probability),
                "affected_components": ["battery", "motors", "sensors"] if maintenance_probability > 0.5 else ["sensors"]
            },
            "confidence": 0.75 + (maintenance_probability * 0.2),  # Higher confidence for higher risk
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return prediction
    
    async def _predict_performance(self, parameters: Dict, time_horizon: str) -> Dict:
        """Predict performance metrics"""
        
        # Get current performance
        current_metrics = await self.get_performance_metrics()
        
        # Simulate performance prediction
        hours = int(time_horizon.replace("h", "")) if "h" in time_horizon else 24
        
        # Predict based on current trends and patterns
        predicted_throughput = current_metrics["throughput"] * np.random.uniform(0.9, 1.2)
        predicted_efficiency = current_metrics["efficiency"] * np.random.uniform(0.85, 1.15)
        
        prediction = {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "performance",
            "time_horizon": time_horizon,
            "results": {
                "predicted_throughput": predicted_throughput,
                "predicted_efficiency": predicted_efficiency,
                "predicted_error_rate": current_metrics["error_rate"] * np.random.uniform(0.8, 1.3),
                "performance_trend": "improving" if predicted_efficiency > current_metrics["efficiency"] else "declining",
                "bottlenecks": ["zone_b_picking"] if predicted_efficiency < 80 else [],
                "optimization_opportunities": ["robot_reassignment", "task_prioritization"]
            },
            "confidence": 0.82,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return prediction
    
    async def _predict_inventory(self, parameters: Dict, time_horizon: str) -> Dict:
        """Predict inventory needs"""
        
        zone_id = parameters.get("zone_id", "zone-a")
        current_inventory = parameters.get("current_inventory", 500)
        
        # Simulate inventory prediction
        hours = int(time_horizon.replace("h", "")) if "h" in time_horizon else 24
        consumption_rate = np.random.uniform(5, 15)  # items per hour
        predicted_consumption = consumption_rate * hours
        
        prediction = {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "inventory",
            "target": zone_id,
            "time_horizon": time_horizon,
            "results": {
                "predicted_inventory_level": max(0, current_inventory - predicted_consumption),
                "predicted_consumption": predicted_consumption,
                "reorder_point": 100,
                "reorder_recommended": current_inventory - predicted_consumption < 100,
                "optimal_reorder_quantity": max(200, predicted_consumption * 2),
                "stockout_risk": "high" if current_inventory - predicted_consumption < 50 else "medium" if current_inventory - predicted_consumption < 100 else "low"
            },
            "confidence": 0.78,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return prediction
    
    async def _predict_throughput(self, parameters: Dict, time_horizon: str) -> Dict:
        """Predict throughput"""
        
        current_throughput = parameters.get("current_throughput", 1000)
        hours = int(time_horizon.replace("h", "")) if "h" in time_horizon else 24
        
        # Simulate throughput prediction
        growth_factor = np.random.uniform(0.95, 1.25)
        predicted_throughput = current_throughput * growth_factor
        
        prediction = {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "throughput",
            "time_horizon": time_horizon,
            "results": {
                "predicted_throughput": predicted_throughput,
                "throughput_trend": "increasing" if growth_factor > 1.0 else "decreasing",
                "capacity_utilization": (predicted_throughput / 2000) * 100,  # Assuming 2000 max capacity
                "peak_hours": ["10:00-12:00", "14:00-16:00"],
                "bottleneck_zones": ["zone_b"] if predicted_throughput > 1500 else []
            },
            "confidence": 0.85,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return prediction
    
    async def _detect_anomalies(self, parameters: Dict) -> Dict:
        """Detect anomalies in current operations"""
        
        # Get recent data
        recent_data = self._get_recent_performance_data(hours=1)
        
        if len(recent_data) < 10:
            return {
                "prediction_id": str(uuid.uuid4()),
                "prediction_type": "anomaly",
                "results": {
                    "anomalies_detected": 0,
                    "anomaly_score": 0.0,
                    "status": "insufficient_data"
                },
                "confidence": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Prepare data for anomaly detection
        features = np.array([[d["throughput"], d["efficiency"], d["error_rate"]] for d in recent_data])
        
        # Fit anomaly detector
        anomaly_scores = self.anomaly_detector.fit_predict(features)
        
        # Count anomalies
        anomaly_count = np.sum(anomaly_scores == -1)
        max_anomaly_score = np.max(np.abs(self.anomaly_detector.decision_function(features)))
        
        prediction = {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "anomaly",
            "results": {
                "anomalies_detected": int(anomaly_count),
                "anomaly_score": float(max_anomaly_score),
                "anomaly_threshold": 0.1,
                "status": "alert" if anomaly_count > 0 else "normal",
                "affected_metrics": ["throughput", "efficiency"] if anomaly_count > 0 else [],
                "recommended_actions": ["investigate_performance", "check_system_health"] if anomaly_count > 0 else []
            },
            "confidence": 0.88,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return prediction
    
    def _calculate_throughput(self) -> float:
        """Calculate current throughput"""
        # Mock calculation based on recent data
        return np.random.uniform(800, 1200)
    
    def _calculate_efficiency(self) -> float:
        """Calculate current efficiency"""
        # Mock efficiency calculation
        return np.random.uniform(75, 95)
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        # Mock error rate calculation
        return np.random.uniform(0.5, 3.0)
    
    def _calculate_uptime(self) -> float:
        """Calculate system uptime"""
        # Mock uptime calculation
        return np.random.uniform(98.5, 99.9)
    
    def _calculate_robot_utilization(self) -> float:
        """Calculate robot utilization"""
        # Mock robot utilization
        return np.random.uniform(60, 90)
    
    def _calculate_zone_utilization(self) -> Dict[str, float]:
        """Calculate zone utilization"""
        zones = ["zone_a", "zone_b", "zone_c", "zone_d"]
        return {zone: np.random.uniform(40, 85) for zone in zones}
    
    def _calculate_average_task_duration(self) -> float:
        """Calculate average task duration"""
        return np.random.uniform(10, 25)  # minutes
    
    def _calculate_battery_efficiency(self) -> float:
        """Calculate battery efficiency"""
        return np.random.uniform(85, 98)
    
    def _get_historical_values(self, metric: str, period: str) -> List[Dict]:
        """Get historical values for a metric"""
        # Mock historical data
        days = int(period.replace("d", "")) if "d" in period else 7
        values = []
        
        for i in range(days * 24):  # Hourly data
            timestamp = datetime.utcnow() - timedelta(hours=i)
            value = np.random.uniform(70, 100)  # Mock values
            
            values.append({
                "timestamp": timestamp.isoformat(),
                "value": value
            })
        
        return values[:100]  # Limit to 100 data points
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation
        recent_avg = np.mean(values[-5:])
        older_avg = np.mean(values[:5])
        
        if recent_avg > older_avg * 1.05:
            return "increasing"
        elif recent_avg < older_avg * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_change_percentage(self, values: List[float]) -> float:
        """Calculate percentage change"""
        if len(values) < 2:
            return 0.0
        
        return ((values[-1] - values[0]) / values[0]) * 100
    
    def _simple_forecast(self, values: List[float], periods: int) -> List[float]:
        """Simple linear forecast"""
        if len(values) < 2:
            return [values[0]] * periods if values else [0] * periods
        
        # Simple linear extrapolation
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        
        forecast = []
        for i in range(periods):
            future_x = len(values) + i
            forecast_value = coeffs[0] * future_x + coeffs[1]
            forecast.append(float(forecast_value))
        
        return forecast
    
    def _detect_anomalies_in_values(self, values: List[float]) -> List[Dict]:
        """Detect anomalies in value series"""
        if len(values) < 10:
            return []
        
        # Use isolation forest for anomaly detection
        values_reshaped = np.array(values).reshape(-1, 1)
        anomaly_labels = self.anomaly_detector.fit_predict(values_reshaped)
        
        anomalies = []
        for i, label in enumerate(anomaly_labels):
            if label == -1:  # Anomaly
                anomalies.append({
                    "index": i,
                    "value": values[i],
                    "anomaly_score": float(self.anomaly_detector.decision_function(values_reshaped)[i])
                })
        
        return anomalies
    
    def _get_maintenance_recommendations(self, probability: float) -> List[str]:
        """Get maintenance recommendations based on probability"""
        if probability > 0.7:
            return ["immediate_inspection", "schedule_maintenance", "prepare_backup_robot"]
        elif probability > 0.4:
            return ["schedule_inspection", "monitor_closely", "prepare_spare_parts"]
        else:
            return ["routine_check", "continue_monitoring"]
    
    def _get_recent_performance_data(self, hours: int = 1) -> List[Dict]:
        """Get recent performance data"""
        # Mock recent data
        data = []
        for i in range(hours * 6):  # Data every 10 minutes
            timestamp = datetime.utcnow() - timedelta(minutes=i * 10)
            data.append({
                "timestamp": timestamp.isoformat(),
                "throughput": np.random.uniform(800, 1200),
                "efficiency": np.random.uniform(75, 95),
                "error_rate": np.random.uniform(0.5, 3.0)
            })
        
        return data
    
    def _initialize_sample_data(self):
        """Initialize with sample historical data"""
        # Generate sample historical data
        for i in range(100):  # 100 data points
            timestamp = datetime.utcnow() - timedelta(hours=i)
            self.historical_data.append({
                "timestamp": timestamp.isoformat(),
                "throughput": np.random.uniform(800, 1200),
                "efficiency": np.random.uniform(75, 95),
                "error_rate": np.random.uniform(0.5, 3.0),
                "robot_utilization": np.random.uniform(60, 90)
            })
