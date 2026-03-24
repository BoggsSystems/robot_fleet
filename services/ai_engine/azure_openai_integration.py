"""
Azure OpenAI Integration for DTDL Generation
"""
import os
import json
import asyncio
from typing import Dict, List, Optional
import openai
from openai import AsyncAzureOpenAI

class AzureOpenAIDTDLGenerator:
    """Enhanced DTDL generator using Azure OpenAI"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://warehouse-ai-openai.openai.azure.com/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        self.api_version = "2024-02-15-preview"
        
        # Initialize client if credentials are available
        self.client = None
        if self.api_key:
            try:
                self.client = AsyncAzureOpenAI(
                    api_key=self.api_key,
                    api_version=self.api_version,
                    azure_endpoint=self.endpoint
                )
                print("✅ Azure OpenAI client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Azure OpenAI client: {e}")
        else:
            print("⚠️ Azure OpenAI credentials not configured - using fallback mode")
    
    async def is_available(self) -> bool:
        """Check if Azure OpenAI service is available"""
        if not self.client:
            return False
        
        try:
            # Test with a simple completion
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"Azure OpenAI not available: {e}")
            return False
    
    async def extract_entities_with_ai(self, user_input: str, model_type: str) -> Dict:
        """Extract DTDL entities using Azure OpenAI"""
        if not await self.is_available():
            return self._fallback_extraction(user_input, model_type)
        
        system_prompt = f"""
        You are a Digital Twin Definition Language (DTDL) expert. Extract entities from user input for {model_type} models.
        
        Analyze this request: "{user_input}"
        
        Extract and return ONLY valid JSON with this structure:
        {{
            "properties": [
                {{"name": "property_name", "type": "string|integer|double|boolean|dateTime", "description": "Description", "unit": "optional_unit"}},
                ...
            ],
            "relationships": [
                {{"name": "relationship_name", "target_model": "TargetModel", "description": "Description"}},
                ...
            ],
            "telemetry": [
                {{"name": "telemetry_name", "type": "string|integer|double|boolean", "description": "Description", "unit": "optional_unit"}},
                ...
            ]
        }}
        
        Rules:
        - Use standard DTDL types: string, integer, double, boolean, dateTime
- Be specific with descriptions
        - Include units where applicable (temperature, area, etc.)
        - Only include relationships to logical target models
        - Return valid JSON only - no explanations
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                entities = json.loads(content)
                return self._validate_entities(entities)
            except json.JSONDecodeError:
                print(f"Failed to parse AI response: {content}")
                return self._fallback_extraction(user_input, model_type)
                
        except Exception as e:
            print(f"AI extraction failed: {e}")
            return self._fallback_extraction(user_input, model_type)
    
    async def generate_complete_dtdl_with_ai(self, user_input: str, model_type: str) -> Dict:
        """Generate complete DTDL model using Azure OpenAI"""
        if not await self.is_available():
            return self._fallback_dtdl_generation(user_input, model_type)
        
        system_prompt = f"""
        You are a Digital Twin Definition Language (DTDL) expert. Create a complete, valid DTDL model for {model_type}.
        
        User request: "{user_input}"
        
        Generate a complete DTDL model following this structure:
        {{
            "@id": "dtmi:com:warehouse:{model_type};1",
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "{model_type.title()}",
            "description": "Description of the {model_type}",
            "contents": [
                // Properties, Relationships, Telemetry, Components
            ]
        }}
        
        Requirements:
        - Valid DTDL v2 syntax
        - Include relevant properties with correct schemas
        - Add appropriate relationships to other models
        - Include useful telemetry for monitoring
        - Add descriptions and display names
        - Use proper units where applicable
        - Return valid JSON only
        
        Common {model_type} properties: name, status, createdAt, location
        Common relationships: contains, connectedTo, assignedTo
        Common telemetry: temperature, humidity, status, activityLevel
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                dtdl_model = json.loads(content)
                return self._validate_dtdl_model(dtdl_model)
            except json.JSONDecodeError:
                print(f"Failed to parse AI DTDL response: {content}")
                return self._fallback_dtdl_generation(user_input, model_type)
                
        except Exception as e:
            print(f"AI DTDL generation failed: {e}")
            return self._fallback_dtdl_generation(user_input, model_type)
    
    def _validate_entities(self, entities: Dict) -> Dict:
        """Validate and clean extracted entities"""
        validated = {
            "properties": [],
            "relationships": [],
            "telemetry": []
        }
        
        # Validate properties
        for prop in entities.get("properties", []):
            if all(k in prop for k in ["name", "type"]):
                validated["properties"].append({
                    "name": prop["name"],
                    "type": prop["type"],
                    "description": prop.get("description", f"Property {prop['name']}"),
                    "unit": prop.get("unit"),
                    "writable": prop.get("writable", True)
                })
        
        # Validate relationships
        for rel in entities.get("relationships", []):
            if all(k in rel for k in ["name", "target_model"]):
                validated["relationships"].append({
                    "name": rel["name"],
                    "target_model": rel["target_model"],
                    "description": rel.get("description", f"Relationship {rel['name']}")
                })
        
        # Validate telemetry
        for tel in entities.get("telemetry", []):
            if all(k in tel for k in ["name", "type"]):
                validated["telemetry"].append({
                    "name": tel["name"],
                    "type": tel["type"],
                    "description": tel.get("description", f"Telemetry {tel['name']}"),
                    "unit": tel.get("unit")
                })
        
        return validated
    
    def _validate_dtdl_model(self, dtdl_model: Dict) -> Dict:
        """Validate and clean DTDL model"""
        required_fields = ["@id", "@type", "@context"]
        
        for field in required_fields:
            if field not in dtdl_model:
                dtdl_model[field] = self._get_default_field(field)
        
        # Ensure contents array exists
        if "contents" not in dtdl_model:
            dtdl_model["contents"] = []
        
        return dtdl_model
    
    def _get_default_field(self, field: str) -> str:
        """Get default value for required DTDL fields"""
        defaults = {
            "@id": "dtmi:com:warehouse:Unknown;1",
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2"
        }
        return defaults.get(field, "")
    
    def _fallback_extraction(self, user_input: str, model_type: str) -> Dict:
        """Fallback to pattern-based extraction"""
        from dtdl_generator import dtdl_generator
        return dtdl_generator.extract_entities_from_input(user_input, model_type)
    
    def _fallback_dtdl_generation(self, user_input: str, model_type: str) -> Dict:
        """Fallback to template-based DTDL generation"""
        from dtdl_generator import dtdl_generator
        
        # Extract entities first
        entities = self._fallback_extraction(user_input, model_type)
        
        # Generate DTDL from entities
        return dtdl_generator.generate_dtdl_model("fallback", model_type, entities)
    
    async def get_suggestions_with_ai(self, dtdl_model: Dict, model_type: str) -> List[str]:
        """Get AI-powered suggestions for DTDL model improvement"""
        if not await self.is_available():
            return self._get_basic_suggestions(dtdl_model, model_type)
        
        system_prompt = f"""
        You are a DTDL expert. Review this {model_type} model and suggest improvements:
        
        {json.dumps(dtdl_model, indent=2)}
        
        Suggest improvements for:
        - Missing common properties for {model_type}
        - Useful telemetry for monitoring
        - Important relationships
        - Best practices
        - Security considerations
        
        Return a JSON array of suggestion strings only.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Review this DTDL model"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                suggestions = json.loads(content)
                return suggestions if isinstance(suggestions, list) else []
            except json.JSONDecodeError:
                return self._get_basic_suggestions(dtdl_model, model_type)
                
        except Exception as e:
            print(f"AI suggestions failed: {e}")
            return self._get_basic_suggestions(dtdl_model, model_type)
    
    def _get_basic_suggestions(self, dtdl_model: Dict, model_type: str) -> List[str]:
        """Get basic template-based suggestions"""
        from dtdl_generator import dtdl_generator
        return dtdl_generator.suggest_improvements(dtdl_model, model_type)

# Global instance
azure_openai_generator = AzureOpenAIDTDLGenerator()
