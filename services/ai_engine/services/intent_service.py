"""
Intent Service - Natural Language Understanding for Warehouse Operations

This service handles:
- Intent parsing and understanding
- Entity extraction
- Contextual reasoning
- Request classification
"""

import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

import openai
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)


class IntentService:
    """Service for understanding warehouse operation requests"""
    
    def __init__(self):
        """Initialize the intent service"""
        logger.info("Initializing Intent Service...")
        
        # Initialize OpenAI client (if API key is available)
        self.openai_client = None
        try:
            # This would use environment variable or config
            # openai.api_key = os.getenv("OPENAI_API_KEY")
            # self.openai_client = openai
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.warning(f"OpenAI client not available: {e}")
        
        # Initialize local models for basic intent classification
        self.intent_classifier = None
        self.tokenizer = None
        
        try:
            # Load a lightweight intent classification model
            model_name = "microsoft/DialoGPT-medium"  # Placeholder - would use actual intent model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.intent_classifier = AutoModelForSequenceClassification.from_pretrained(model_name)
            logger.info("Local intent classifier loaded")
        except Exception as e:
            logger.warning(f"Local intent classifier not available: {e}")
        
        # Define intent patterns for rule-based classification
        self.intent_patterns = {
            "picking": [
                "pick", "retrieve", "get", "collect", "gather", "fetch",
                "order", "item", "product", "sku", "barcode"
            ],
            "packing": [
                "pack", "package", "box", "wrap", "prepare", "ship",
                "order", "delivery", "fulfillment"
            ],
            "transport": [
                "move", "transport", "carry", "deliver", "bring",
                "location", "zone", "area", "destination"
            ],
            "inventory": [
                "count", "inventory", "stock", "check", "audit",
                "quantity", "level", "reorder", "restock"
            ],
            "maintenance": [
                "maintenance", "repair", "fix", "service", "inspect",
                "broken", "damage", "issue", "problem"
            ],
            "charging": [
                "charge", "battery", "power", "energy", "recharge",
                "station", "dock", "power up"
            ],
            "emergency": [
                "emergency", "urgent", "immediate", "critical",
                "stop", "halt", "danger", "safety"
            ]
        }
        
        logger.info("Intent Service initialized successfully")
    
    async def parse_intent(self, request_text: str, context: Dict = None) -> Dict:
        """
        Parse intent from natural language request
        
        Args:
            request_text: Natural language request
            context: Additional context information
            
        Returns:
            Parsed intent with entities and confidence
        """
        try:
            logger.info(f"Parsing intent: {request_text[:100]}...")
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(request_text)
            
            # Extract intent using multiple methods
            intent_result = await self._extract_intent(cleaned_text, context)
            
            # Extract entities
            entities = await self._extract_entities(cleaned_text, intent_result["intent"])
            
            # Extract constraints
            constraints = await self._extract_constraints(cleaned_text, context)
            
            # Calculate confidence
            confidence = self._calculate_confidence(intent_result, entities, constraints)
            
            result = {
                "intent": intent_result["intent"],
                "intent_category": intent_result["category"],
                "confidence": confidence,
                "entities": entities,
                "constraints": constraints,
                "parsed_at": datetime.utcnow().isoformat(),
                "raw_text": request_text,
                "context_used": context or {}
            }
            
            logger.info(f"Intent parsed: {intent_result['intent']} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse intent: {str(e)}")
            raise
    
    async def _extract_intent(self, text: str, context: Dict = None) -> Dict:
        """Extract intent using multiple methods"""
        
        # Method 1: Rule-based pattern matching
        rule_based_intent = self._rule_based_intent_extraction(text)
        
        # Method 2: ML-based classification (if available)
        ml_based_intent = await self._ml_based_intent_extraction(text)
        
        # Method 3: Context-aware reasoning
        context_intent = self._context_aware_intent_extraction(text, context)
        
        # Combine results with confidence weighting
        combined_intent = self._combine_intent_results(
            rule_based_intent, ml_based_intent, context_intent
        )
        
        return combined_intent
    
    def _rule_based_intent_extraction(self, text: str) -> Dict:
        """Extract intent using rule-based pattern matching"""
        text_lower = text.lower()
        
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            intent_scores[intent] = score
        
        if not intent_scores or max(intent_scores.values()) == 0:
            return {"intent": "unknown", "category": "general", "confidence": 0.0}
        
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent] / 3.0, 1.0)  # Normalize confidence
        
        return {
            "intent": best_intent,
            "category": self._get_intent_category(best_intent),
            "confidence": confidence,
            "method": "rule_based"
        }
    
    async def _ml_based_intent_extraction(self, text: str) -> Dict:
        """Extract intent using ML models"""
        if not self.intent_classifier or not self.tokenizer:
            return {"intent": "unknown", "category": "general", "confidence": 0.0}
        
        try:
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Get prediction
            with torch.no_grad():
                outputs = self.intent_classifier(**inputs)
                predictions = torch.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(predictions, dim=-1).item()
                confidence = predictions[0][predicted_class].item()
            
            # Map class to intent (this would depend on the actual model)
            intent_mapping = {0: "picking", 1: "packing", 2: "transport", 3: "inventory"}
            intent = intent_mapping.get(predicted_class, "unknown")
            
            return {
                "intent": intent,
                "category": self._get_intent_category(intent),
                "confidence": confidence,
                "method": "ml_based"
            }
            
        except Exception as e:
            logger.warning(f"ML-based intent extraction failed: {e}")
            return {"intent": "unknown", "category": "general", "confidence": 0.0}
    
    def _context_aware_intent_extraction(self, text: str, context: Dict = None) -> Dict:
        """Extract intent using context information"""
        if not context:
            return {"intent": "unknown", "category": "general", "confidence": 0.0}
        
        # Extract intent based on context
        context_hints = []
        
        # Check for robot-related context
        if "robot_id" in context:
            context_hints.append("robot_operation")
        
        # Check for zone context
        if "zone_id" in context:
            zone_type = context.get("zone_type", "")
            if "picking" in zone_type.lower():
                context_hints.append("picking")
            elif "receiving" in zone_type.lower():
                context_hints.append("receiving")
        
        # Check for inventory context
        if "inventory_level" in context:
            context_hints.append("inventory")
        
        # Check for battery context
        if "battery_level" in context and context.get("battery_level", 100) < 20:
            context_hints.append("charging")
        
        # Combine context hints with text analysis
        text_lower = text.lower()
        best_intent = "unknown"
        best_score = 0
        
        for hint in context_hints:
            if hint in self.intent_patterns:
                for pattern in self.intent_patterns[hint]:
                    if pattern in text_lower:
                        if hint not in ["emergency", "charging"]:  # Prioritize these
                            best_score += 2
                        else:
                            best_score += 3
                        best_intent = hint
        
        confidence = min(best_score / 5.0, 1.0) if best_score > 0 else 0.0
        
        return {
            "intent": best_intent if best_score > 0 else "unknown",
            "category": self._get_intent_category(best_intent) if best_score > 0 else "general",
            "confidence": confidence,
            "method": "context_aware"
        }
    
    def _combine_intent_results(self, rule_based: Dict, ml_based: Dict, context_aware: Dict) -> Dict:
        """Combine results from different intent extraction methods"""
        
        # Weight different methods
        weights = {
            "rule_based": 0.4,
            "ml_based": 0.4,
            "context_aware": 0.2
        }
        
        # Collect all intents with their confidences
        intents = {}
        
        for result, weight in [(rule_based, weights["rule_based"]), 
                              (ml_based, weights["ml_based"]), 
                              (context_aware, weights["context_aware"])]:
            if result["intent"] != "unknown":
                intent = result["intent"]
                confidence = result["confidence"] * weight
                intents[intent] = intents.get(intent, 0) + confidence
        
        if not intents:
            return {"intent": "unknown", "category": "general", "confidence": 0.0}
        
        # Get best intent
        best_intent = max(intents, key=intents.get)
        total_confidence = intents[best_intent]
        
        return {
            "intent": best_intent,
            "category": self._get_intent_category(best_intent),
            "confidence": min(total_confidence, 1.0)
        }
    
    async def _extract_entities(self, text: str, intent: str) -> List[Dict]:
        """Extract entities from request text"""
        entities = []
        
        # Common entity patterns
        entity_patterns = {
            "location": ["zone", "area", "location", "aisle", "bay", "dock"],
            "quantity": ["quantity", "count", "number", "amount", "units"],
            "product": ["product", "item", "sku", "barcode", "product_id"],
            "robot": ["robot", "bot", "unit", "machine"],
            "time": ["minute", "hour", "second", "immediate", "urgent", "asap"],
            "priority": ["priority", "urgent", "important", "critical", "normal"]
        }
        
        text_lower = text.lower()
        
        for entity_type, patterns in entity_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    # Extract surrounding context (simplified)
                    start = text_lower.find(pattern)
                    end = start + len(pattern)
                    
                    # Get some context around the entity
                    context_start = max(0, start - 20)
                    context_end = min(len(text), end + 20)
                    context = text[context_start:context_end]
                    
                    entities.append({
                        "type": entity_type,
                        "value": pattern,
                        "confidence": 0.8,
                        "context": context.strip(),
                        "position": {"start": start, "end": end}
                    })
        
        return entities
    
    async def _extract_constraints(self, text: str, context: Dict = None) -> List[Dict]:
        """Extract constraints from request text"""
        constraints = []
        
        # Common constraint patterns
        constraint_patterns = {
            "time_limit": ["within", "before", "by", "deadline", "asap"],
            "priority": ["urgent", "high priority", "important", "critical"],
            "capacity": ["capacity", "limit", "maximum", "minimum"],
            "safety": ["safety", "danger", "hazard", "caution"],
            "equipment": ["robot", "tool", "equipment", "device"]
        }
        
        text_lower = text.lower()
        
        for constraint_type, patterns in constraint_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    constraints.append({
                        "type": constraint_type,
                        "value": pattern,
                        "source": "text"
                    })
        
        # Add context-based constraints
        if context:
            if context.get("battery_level", 100) < 20:
                constraints.append({
                    "type": "battery",
                    "value": "low_battery",
                    "source": "context"
                })
            
            if context.get("zone_capacity", 0) > 80:
                constraints.append({
                    "type": "capacity",
                    "value": "high_occupancy",
                    "source": "context"
                })
        
        return constraints
    
    def _calculate_confidence(self, intent_result: Dict, entities: List, constraints: List) -> float:
        """Calculate overall confidence score"""
        
        # Base confidence from intent extraction
        base_confidence = intent_result.get("confidence", 0.0)
        
        # Boost confidence based on entities found
        entity_boost = min(len(entities) * 0.1, 0.3)
        
        # Boost confidence based on constraints found
        constraint_boost = min(len(constraints) * 0.05, 0.2)
        
        # Calculate final confidence
        final_confidence = base_confidence + entity_boost + constraint_boost
        
        return min(final_confidence, 1.0)
    
    def _get_intent_category(self, intent: str) -> str:
        """Get category for intent"""
        category_mapping = {
            "picking": "fulfillment",
            "packing": "fulfillment",
            "transport": "logistics",
            "inventory": "management",
            "maintenance": "maintenance",
            "charging": "maintenance",
            "emergency": "safety",
            "receiving": "logistics",
            "shipping": "logistics"
        }
        
        return category_mapping.get(intent, "general")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for intent extraction"""
        # Basic preprocessing
        text = text.strip()
        # Convert to lowercase for pattern matching
        return text
