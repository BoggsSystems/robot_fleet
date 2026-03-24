from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import re

class DTDLConversationRequest(BaseModel):
    conversation_id: str
    user_input: str
    context: Optional[Dict] = {}
    model_type: Optional[str] = "warehouse"  # warehouse, zone, robot, etc.

class DTDLProperty(BaseModel):
    name: str
    type: str
    description: str
    unit: Optional[str] = None
    writable: bool = True
    enum_values: Optional[List[str]] = None

class DTDLRelationship(BaseModel):
    name: str
    target_model: str
    multiplicity: Optional[str] = "single"
    description: str

class DTDLTelemetry(BaseModel):
    name: str
    type: str
    unit: Optional[str] = None
    description: str

class DTDLComponent(BaseModel):
    name: str
    model_ref: str
    description: str

class DTDLGenerator:
    def __init__(self):
        self.conversation_context = {}
        self.dtdl_templates = {
            "warehouse": {
                "base_properties": ["name", "totalArea", "status", "createdAt"],
                "common_relationships": ["contains", "manages"],
                "common_telemetry": ["temperature", "humidity", "occupancy"]
            },
            "zone": {
                "base_properties": ["name", "zoneType", "capacity", "currentLoad"],
                "common_relationships": ["contains", "connectedTo"],
                "common_telemetry": ["temperature", "itemCount", "activityLevel"]
            },
            "robot": {
                "base_properties": ["name", "robotType", "batteryLevel", "status", "currentTask"],
                "common_relationships": ["assignedTo", "connectedTo"],
                "common_telemetry": ["batteryVoltage", "positionX", "positionY", "speed", "loadWeight"]
            }
        }
    
    def extract_entities_from_input(self, user_input: str, model_type: str) -> Dict:
        """Extract properties, relationships, and telemetry from natural language"""
        
        entities = {
            "properties": [],
            "relationships": [],
            "telemetry": [],
            "components": []
        }
        
        # Enhanced keyword mapping
        property_keywords = {
            "name": ["name", "title", "label", "identifier"],
            "area": ["area", "size", "space", "square feet", "sqft", "square meters"],
            "status": ["status", "state", "condition", "active", "inactive"],
            "capacity": ["capacity", "limit", "max", "maximum"],
            "temperature": ["temperature", "temp", "heat", "thermal"],
            "humidity": ["humidity", "moisture", "dampness"],
            "occupancy": ["occupancy", "occupied", "utilization", "usage"],
            "inventory": ["inventory", "stock", "items", "products", "goods"],
            "battery": ["battery", "power", "charge", "energy"],
            "position": ["position", "location", "coordinates", "x", "y", "z"],
            "speed": ["speed", "velocity", "rate", "pace"],
            "load": ["load", "weight", "cargo", "burden"]
        }
        
        relationship_keywords = {
            "contains": ["contains", "has", "includes", "holds", "stores"],
            "connected": ["connected", "linked", "related", "attached"],
            "manages": ["manages", "controls", "supervises", "operates"],
            "assigned": ["assigned", "allocated", "distributed", "placed"],
            "monitors": ["monitors", "tracks", "observes", "watches"]
        }
        
        telemetry_keywords = {
            "temperature": ["temperature", "temp", "thermal", "heat"],
            "humidity": ["humidity", "moisture", "dampness"],
            "occupancy": ["occupancy", "usage", "utilization"],
            "activity": ["activity", "motion", "movement", "operations"],
            "battery": ["battery", "power", "charge", "voltage"],
            "position": ["position", "location", "coordinates", "gps"],
            "speed": ["speed", "velocity", "rate"],
            "load": ["load", "weight", "cargo", "pressure"],
            "flow": ["flow", "rate", "throughput", "processing"],
            "count": ["count", "quantity", "number", "items"]
        }
        
        # Enhanced pattern matching
        user_input_lower = user_input.lower()
        
        # Extract properties with enhanced patterns
        for prop_name, keywords in property_keywords.items():
            for keyword in keywords:
                # Multiple pattern matching
                patterns = [
                    rf"{keyword}\s+(?:property|field|attribute)",
                    rf"(?:add|include|has|need|should have|requires)\s+{keyword}",
                    rf"{keyword}\s+(?:is|should be)\s+(?:a\s+)?(\w+)",
                    rf"{keyword}[:\s]*(\w+)",  # For "name: string"
                    rf"{keyword}\s+(\w+)"  # For "temperature monitoring"
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, user_input_lower)
                    for match in matches:
                        if isinstance(match, tuple):
                            prop_value = match[1] if len(match) > 1 else "string"
                        else:
                            prop_value = self._infer_type_from_context(match, user_input_lower)
                        
                        # Avoid duplicates
                        if not any(p["name"] == prop_name for p in entities["properties"]):
                            entities["properties"].append({
                                "name": prop_name,
                                "type": prop_value,
                                "description": f"Property {prop_name} of type {prop_value}",
                                "unit": self._get_unit_for_property(prop_name)
                            })
        
        # Extract relationships
        for rel_name, keywords in relationship_keywords.items():
            for keyword in keywords:
                patterns = [
                    rf"(\w+)\s+(?:{keyword}|{keyword}s?)\s+(\w+)",
                    rf"{keyword}s?\s+(?:from|to|with|by)\s+(\w+)",
                    rf"(\w+)\s+(?:is|should be)\s+{keyword}s?\s+(?:to|with|by)\s+(\w+)"
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, user_input_lower)
                    for match in matches:
                        source = match[0] if len(match) > 1 else model_type
                        target = match[1] if len(match) > 1 else self._infer_target_from_context(match, user_input_lower)
                        
                        if not any(r["name"] == rel_name for r in entities["relationships"]):
                            entities["relationships"].append({
                                "name": rel_name,
                                "target_model": target.title(),
                                "description": f"Relationship {rel_name} from {source} to {target}"
                            })
        
        # Extract telemetry
        for tel_name, keywords in telemetry_keywords.items():
            for keyword in keywords:
                patterns = [
                    rf"(?:monitor|track|measure|observe|watch|send|transmit|report)\s+{keyword}",
                    rf"{keyword}\s+(?:monitoring|tracking|data|telemetry|sensor)",
                    rf"{keyword}\s+(?:levels|readings|measurements|values)"
                ]
                
                for pattern in patterns:
                    if re.search(pattern, user_input_lower):
                        if not any(t["name"] == tel_name for t in entities["telemetry"]):
                            entities["telemetry"].append({
                                "name": tel_name,
                                "type": self._infer_type_from_context(tel_name, user_input_lower),
                                "description": f"Telemetry {tel_name}",
                                "unit": self._get_unit_for_property(tel_name)
                            })
        
        return entities
    
    def _infer_type_from_context(self, entity: str, context: str) -> str:
        """Infer data type from context clues"""
        type_mapping = {
            "string": ["name", "title", "label", "status", "type", "description"],
            "integer": ["area", "capacity", "count", "quantity", "level", "limit", "max"],
            "double": ["temperature", "humidity", "percentage", "speed", "weight", "load", "rate"],
            "boolean": ["active", "enabled", "flag", "status"],
            "dateTime": ["time", "date", "timestamp", "created", "updated"]
        }
        
        context_lower = context.lower()
        
        for data_type, keywords in type_mapping.items():
            if any(keyword in context_lower for keyword in keywords):
                return data_type
        
        return "string"  # Default
    
    def _infer_target_from_context(self, match: str, context: str) -> str:
        """Infer target model from context"""
        context_lower = context.lower()
        
        # Common model mappings
        model_mappings = {
            "zone": ["zone", "area", "section", "region", "location"],
            "robot": ["robot", "bots", "automation", "machines"],
            "sensor": ["sensor", "device", "iot", "monitor"],
            "warehouse": ["warehouse", "facility", "building", "structure"]
        }
        
        for model, keywords in model_mappings.items():
            if any(keyword in context_lower for keyword in keywords):
                return model
        
        return "Unknown"
    
    def _get_unit_for_property(self, property_name: str) -> Optional[str]:
        """Get appropriate unit for property"""
        unit_mapping = {
            "temperature": "degreeCelsius",
            "humidity": "percent",
            "area": "squareFeet",
            "capacity": "count",
            "speed": "metersPerSecond",
            "load": "kilograms",
            "battery": "percent",
            "occupancy": "percent"
        }
        return unit_mapping.get(property_name)
    
    def _get_unit_for_telemetry(self, telemetry_name: str) -> Optional[str]:
        """Get appropriate unit for telemetry"""
        return self._get_unit_for_property(telemetry_name)
    
    def _infer_type(self, type_hint: str) -> str:
        """Infer DTDL type from natural language"""
        type_mapping = {
            "string": ["string", "text", "name", "description", "status", "type"],
            "integer": ["integer", "number", "count", "capacity", "area", "level", "quantity"],
            "double": ["double", "float", "decimal", "temperature", "humidity", "percentage", "weight"],
            "boolean": ["boolean", "bool", "flag", "enabled", "active"],
            "dateTime": ["datetime", "date", "time", "timestamp", "created", "updated"]
        }
        
        type_hint = type_hint.lower()
        for dtdl_type, keywords in type_mapping.items():
            if any(keyword in type_hint for keyword in keywords):
                return dtdl_type
        
        return "string"  # Default fallback
    
    def generate_dtdl_model(self, conversation_id: str, model_type: str, entities: Dict) -> Dict:
        """Generate complete DTDL model from conversation entities"""
        
        model_id = f"dtmi:com:warehouse:{model_type.title()};1"
        
        # Base model structure
        dtdl_model = {
            "@id": model_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": model_type.title(),
            "description": f"Digital twin model for {model_type}",
            "contents": []
        }
        
        # Add properties
        for prop in entities.get("properties", []):
            dtdl_model["contents"].append({
                "@type": "Property",
                "name": prop["name"],
                "schema": prop["type"],
                "writable": prop.get("writable", True),
                "displayName": prop["name"].replace("_", " ").title(),
                "description": prop.get("description", f"Property {prop['name']}")
            })
        
        # Add relationships
        for rel in entities.get("relationships", []):
            dtdl_model["contents"].append({
                "@type": "Relationship",
                "name": rel["name"],
                "target": rel["target_model"],
                "displayName": rel["name"].replace("_", " ").title(),
                "description": rel.get("description", f"Relationship {rel['name']}")
            })
        
        # Add telemetry
        for tel in entities.get("telemetry", []):
            dtdl_model["contents"].append({
                "@type": "Telemetry",
                "name": tel["name"],
                "schema": tel["type"],
                "displayName": tel["name"].replace("_", " ").title(),
                "description": tel.get("description", f"Telemetry {tel['name']}")
            })
        
        return dtdl_model
    
    def suggest_improvements(self, dtdl_model: Dict, model_type: str) -> List[str]:
        """Suggest improvements based on best practices"""
        suggestions = []
        
        contents = dtdl_model.get("contents", [])
        properties = [c for c in contents if c.get("@type") == "Property"]
        relationships = [c for c in contents if c.get("@type") == "Relationship"]
        telemetry = [c for c in contents if c.get("@type") == "Telemetry"]
        
        # Check for common missing properties
        template = self.dtdl_templates.get(model_type, {})
        for prop in template.get("base_properties", []):
            if not any(p["name"] == prop for p in properties):
                suggestions.append(f"Consider adding '{prop}' property - common for {model_type} models")
        
        # Check for missing telemetry
        for tel in template.get("common_telemetry", []):
            if not any(t["name"] == tel for t in telemetry):
                suggestions.append(f"Consider adding '{tel}' telemetry - useful for monitoring {model_type}")
        
        # Check for relationships
        if len(relationships) == 0 and model_type != "robot":
            suggestions.append(f"Consider adding relationships to connect {model_type} with other models")
        
        # Check for description completeness
        for content in contents:
            if not content.get("description"):
                suggestions.append(f"Add description for '{content.get('name', 'unnamed')}' {content.get('@type', 'content')}")
        
        return suggestions
    
    def validate_dtdl_model(self, dtdl_model: Dict) -> Dict:
        """Validate DTDL model against schema and best practices"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = ["@id", "@type", "@context"]
        for field in required_fields:
            if field not in dtdl_model:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["valid"] = False
        
        # Check contents structure
        contents = dtdl_model.get("contents", [])
        for i, content in enumerate(contents):
            if "@type" not in content:
                validation_result["errors"].append(f"Content {i} missing @type")
                validation_result["valid"] = False
            
            if "name" not in content:
                validation_result["errors"].append(f"Content {i} missing name")
                validation_result["valid"] = False
        
        return validation_result

# Initialize the generator
dtdl_generator = DTDLGenerator()
