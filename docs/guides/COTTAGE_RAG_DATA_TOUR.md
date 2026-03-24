# 🏠 Cottage RAG Data Flow Tour

## 📊 **Database Structure**

### **Shared Knowledge Table** (`documents`)
```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,              -- "robot_quadruped", "zone_kitchen"
    content TEXT NOT NULL,            -- JSON document with full details
    metadata TEXT NOT NULL,           -- {"type": "robot", "zone_name": "kitchen"}
    client_id TEXT NOT NULL,          -- "shared" or "cot_12345678"
    scope TEXT NOT NULL,              -- "shared" or "client_specific"
    created_at TEXT NOT NULL,         -- "2024-03-20T16:00:00Z"
    access_count INTEGER DEFAULT 0,    -- Usage tracking for optimization
    effectiveness_score REAL DEFAULT 1.0,
    embedding BLOB                     -- Vector embedding for similarity search
);
```

### **Client Registry Table** (`clients`)
```sql
CREATE TABLE clients (
    client_id TEXT PRIMARY KEY,       -- "cot_12345678"
    config TEXT NOT NULL,             -- JSON client configuration
    created_at TEXT NOT NULL,         -- Registration timestamp
    last_activity TEXT NOT NULL,      -- Last query timestamp
    query_count INTEGER DEFAULT 0,     -- Total queries processed
    success_rate REAL DEFAULT 0.0     -- Query success rate
);
```

### **Client-Specific Table** (`personal_documents`)
```sql
CREATE TABLE personal_documents (
    id TEXT PRIMARY KEY,              -- "user_preference_morning_coffee"
    content TEXT NOT NULL,            -- User preferences and learned patterns
    metadata TEXT NOT NULL,           -- {"type": "preference", "category": "daily_routine"}
    created_at TEXT NOT NULL,         -- When learned
    access_count INTEGER DEFAULT 0,    -- Usage frequency
    effectiveness_score REAL DEFAULT 1.0
);
```

## 🗄️ **Cottage Data Population**

### **1. Shared Knowledge Documents**
```python
# Robot Capabilities
robot_quadruped = {
    "id": "robot_quadruped",
    "content": """
    {
        "type": "quadruped",
        "description": "Four-legged robot with outdoor navigation",
        "capabilities": ["outdoor_navigation", "rough_terrain", "payload_transport"],
        "limitations": ["fine_manipulation", "indoor_narrow_spaces"],
        "preferred_tasks": ["outdoor_delivery", "patrol", "heavy_transport"],
        "specifications": {
            "payload_capacity": "12.5kg",
            "battery_life": "2-3 hours",
            "speed": "1.5 m/s"
        }
    }
    """,
    "metadata": {
        "type": "robot",
        "category": "capabilities",
        "robot_type": "quadruped",
        "scope": "shared"
    },
    "client_id": "shared",
    "scope": "shared"
}

# Cottage Zones
zone_kitchen = {
    "id": "zone_kitchen",
    "content": """
    {
        "name": "kitchen",
        "type": "indoor",
        "description": "Main kitchen area with cooking, food storage, and dining spaces",
        "landmarks": ["refrigerator", "stove", "sink", "dishwasher", "coffee_maker"],
        "common_tasks": ["food_preparation", "cooking", "cleaning", "dishwashing"],
        "constraints": ["no_liquid_spills", "keep_appliances_clear"],
        "connectivity": ["living_room", "dining_area"],
        "typical_items": ["groceries", "cookware", "dishes", "cleaning_supplies"]
    }
    """,
    "metadata": {
        "type": "zone",
        "category": "cottage_layout",
        "zone_name": "kitchen",
        "zone_type": "indoor",
        "scope": "client_specific"
    },
    "client_id": "cot_12345678",
    "scope": "client_specific"
}

# Mission Templates
mission_inspection = {
    "id": "mission_inspection",
    "content": """
    {
        "type": "inspection",
        "description": "Systematic inspection of areas and equipment",
        "procedures": [
            "Define inspection area and objectives",
            "Select appropriate robot based on terrain",
            "Configure inspection parameters",
            "Execute inspection with systematic coverage",
            "Document findings and anomalies"
        ],
        "robot_recommendations": {
            "indoor": "humanoid",
            "outdoor": "quadruped",
            "aerial": "drone"
        },
        "common_variations": [
            "qr_code_scan",
            "safety_inspection",
            "inventory_check",
            "damage_assessment"
        ]
    }
    """,
    "metadata": {
        "type": "mission",
        "category": "templates",
        "mission_type": "inspection",
        "scope": "shared"
    },
    "client_id": "shared",
    "scope": "shared"
}
```

### **2. Cottage-Specific Documents**
```python
# Cottage Layout
cottage_layout = {
    "id": "cottage_floor_plan",
    "content": """
    The cottage follows a traditional layout with central hallway connecting all main rooms.
    
    Room Dimensions:
    - Kitchen: 15' x 12' with island and dining area
    - Living Room: 18' x 14' with open concept to dining
    - Bedroom: 14' x 12' with walk-in closet
    - Bathroom: 8' x 6' with shower/tub combination
    - Garage: 20' x 12' with workshop area
    - Dock: 12' x 8' covered loading area
    
    Navigation:
    - Central hallway provides access to all rooms
    - Kitchen connects to living room through open archway
    - Master bedroom has private bathroom access
    - Garage connects to house through mudroom
    """,
    "metadata": {
        "type": "layout",
        "category": "navigation",
        "scope": "client_specific"
    },
    "client_id": "cot_12345678",
    "scope": "client_specific"
}

# Cottage Procedures
cottage_procedures = {
    "id": "cottage_morning_routine",
    "content": """
    {
        "name": "morning_preparation_procedure",
        "description": "Morning routine preparation procedures",
        "steps": [
            "Check overnight security status",
            "Prepare coffee and breakfast areas",
            "Review daily schedule and priorities",
            "Check weather and outdoor conditions",
            "Prepare robots for daily tasks"
        ],
        "robot_involvement": {
            "humanoid": "Prepare kitchen area and breakfast setup",
            "quadruped": "Check outdoor conditions and weather station",
            "drone": "Quick aerial survey of property"
        }
    }
    """,
    "metadata": {
        "type": "procedure",
        "category": "cottage_specific",
        "procedure_name": "morning_preparation",
        "scope": "client_specific"
    },
    "client_id": "cot_12345678",
    "scope": "client_specific"
}
```

## 🔍 **Vector Embedding Process**

### **Embedding Generation**
```python
# For each document, generate vector embedding
if EMBEDDINGS_AVAILABLE and self.embedding_model:
    doc.embedding = self.embedding_model.encode(doc.content).tolist()
    
    # Example embedding for "kitchen" zone document:
    # [0.1234, -0.5678, 0.9012, ..., 0.3456]  # 384-dimensional vector
```

### **Similarity Calculation**
```python
# Query: "Scan kitchen for QR codes"
query_embedding = embedding_model.encode("Scan kitchen for QR codes")

# Compare with document embeddings
similarity_scores = cosine_similarity(
    [query_embedding], 
    [kitchen_embedding, inspection_embedding, robot_embedding]
)

# Results:
# - zone_kitchen: 0.92 (high similarity - contains "kitchen")
# - mission_inspection: 0.87 (medium similarity - contains "scan", "qr")
# - robot_quadruped: 0.45 (low similarity - general robot info)
```

## 🔄 **Query Processing Flow**

### **1. User Query Input**
```python
user_query = "Scan the kitchen area for QR codes and report findings"
client_id = "cot_12345678"
```

### **2. Query Embedding**
```python
# Generate embedding for user query
query_embedding = embedding_model.encode(user_query)
# Vector: [0.2345, -0.6789, 0.8901, ..., 0.4567]
```

### **3. Database Search**
```python
# SQL query for similarity search
await db.execute("""
    SELECT id, content, metadata, client_id, scope, embedding,
           1 - (ABS(embedding - ?) / 
               (SELECT MAX(ABS(embedding - ?)) FROM documents 
                WHERE client_id IN ('shared', ?))) as similarity_score
    FROM documents 
    WHERE client_id IN ('shared', ?)
    ORDER BY similarity_score DESC
    LIMIT ?
""", (query_embedding, query_embedding, client_id, client_id, 5))
```

### **4. Results Ranking**
```python
search_results = [
    {
        "id": "zone_kitchen",
        "content": kitchen_zone_json,
        "metadata": {"type": "zone", "zone_name": "kitchen"},
        "similarity_score": 0.92,
        "client_id": "cot_12345678",
        "scope": "client_specific"
    },
    {
        "id": "mission_inspection",
        "content": inspection_mission_json,
        "metadata": {"type": "mission", "mission_type": "inspection"},
        "similarity_score": 0.87,
        "client_id": "shared",
        "scope": "shared"
    },
    {
        "id": "robot_quadruped",
        "content": quadruped_robot_json,
        "metadata": {"type": "robot", "robot_type": "quadruped"},
        "similarity_score": 0.78,
        "client_id": "shared",
        "scope": "shared"
    }
]
```

## 🧠 **Context Assembly for AI**

### **Context Building**
```python
def build_context_for_ai(search_results, user_query):
    context = {
        "cottage_knowledge": [],
        "robot_capabilities": [],
        "mission_templates": [],
        "procedures": []
    }
    
    for result in search_results:
        content = json.loads(result["content"])
        metadata = result["metadata"]
        
        if metadata["type"] == "zone":
            context["cottage_knowledge"].append(content)
        elif metadata["type"] == "robot":
            context["robot_capabilities"].append(content)
        elif metadata["type"] == "mission":
            context["mission_templates"].append(content)
        elif metadata["type"] == "procedure":
            context["procedures"].append(content)
    
    return context

# Built context:
context = {
    "cottage_knowledge": [
        {
            "name": "kitchen",
            "landmarks": ["refrigerator", "stove", "sink"],
            "common_tasks": ["food_preparation", "cleaning"],
            "typical_items": ["groceries", "dishes"]
        }
    ],
    "robot_capabilities": [
        {
            "type": "quadruped",
            "capabilities": ["outdoor_navigation", "payload_transport"],
            "preferred_tasks": ["patrol", "delivery"]
        }
    ],
    "mission_templates": [
        {
            "type": "inspection",
            "procedures": ["Define area", "Select robot", "Execute inspection"],
            "robot_recommendations": {"indoor": "humanoid", "outdoor": "quadruped"}
        }
    ]
}
```

## 🎯 **AI Intent Processing with Context**

### **Enhanced Prompt Building**
```python
def build_enhanced_prompt(user_query, context):
    return f"""
COTTAGE CONTEXT:
You are operating in a residential cottage environment.

AVAILABLE ZONES:
{json.dumps(context['cottage_knowledge'], indent=2)}

ROBOT CAPABILITIES:
{json.dumps(context['robot_capabilities'], indent=2)}

MISSION TEMPLATES:
{json.dumps(context['mission_templates'], indent=2)}

USER QUERY: {user_query}

Using this cottage-specific knowledge, parse the user's intent and generate an appropriate mission plan.
Consider:
1. Which zone is involved based on landmarks and connectivity
2. Which robot is best suited for the task
3. What procedures and templates apply
4. Any cottage-specific constraints or preferences
"""
```

### **AI Response Generation**
```python
# OpenAI API call with enhanced context
response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": enhanced_prompt},
        {"role": "user", "content": user_query}
    ]
)

# AI Response:
{
    "mission_type": "inspection",
    "objective": "Scan kitchen area for QR codes and report findings",
    "source_zone": "kitchen",
    "destination_zone": "kitchen",
    "required_capabilities": ["inspection", "qr_scanning"],
    "recommended_robot": "quadruped",
    "rationale": "Kitchen zone identified, quadruped suitable for indoor inspection with QR scanning capability",
    "steps": [
        "Navigate to kitchen area",
        "Systematically scan for QR codes using camera",
        "Document all QR codes found and their locations",
        "Generate inspection report with findings"
    ]
}
```

## 📈 **Learning and Adaptation**

### **Interaction Recording**
```python
# Record user interaction for learning
interaction = {
    "interaction_id": str(uuid4()),
    "client_id": "cot_12345678",
    "query": "Scan the kitchen area for QR codes",
    "response": ai_response,
    "context_used": context_summary,
    "success": True,
    "timestamp": datetime.now().isoformat(),
    "feedback": None  # To be filled by user feedback
}

# Store in client-specific database
await client_db.execute("""
    INSERT INTO user_interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    interaction["interaction_id"],
    interaction["client_id"],
    interaction["query"],
    json.dumps(interaction["response"]),
    json.dumps(interaction["context_used"]),
    interaction["success"],
    interaction["timestamp"],
    interaction["feedback"]
))
```

### **Pattern Learning**
```python
# Update client learning patterns
def update_learning_patterns(interaction):
    # Extract user terminology
    query_words = interaction["query"].lower().split()
    user_terms = [word for word in query_words if len(word) > 3]
    
    # Update user-specific terms
    for term in user_terms:
        if term not in learned_patterns["user_terms"]:
            learned_patterns["user_terms"][term] = {"count": 0, "contexts": []}
        learned_patterns["user_terms"][term]["count"] += 1
        learned_patterns["user_terms"][term]["contexts"].append(interaction["context"])
    
    # Update mission type preferences
    mission_type = interaction["response"]["mission_type"]
    if mission_type not in learned_patterns["frequent_missions"]:
        learned_patterns["frequent_missions"][mission_type] = 0
    learned_patterns["frequent_missions"][mission_type"] += 1
```

## 🔄 **Complete Data Flow Summary**

```
1. USER QUERY
   "Scan kitchen for QR codes"
   ↓
2. QUERY EMBEDDING
   Vector: [0.2345, -0.6789, 0.8901, ...]
   ↓
3. DATABASE SEARCH
   - Search shared + client documents
   - Calculate similarity scores
   - Rank by relevance
   ↓
4. CONTEXT ASSEMBLY
   - Kitchen zone details
   - Robot capabilities
   - Mission templates
   - Cottage procedures
   ↓
5. AI ENHANCED PROMPT
   - Cottage context + user query
   - Environment-specific knowledge
   - Learned user patterns
   ↓
6. AI RESPONSE
   - Mission type: inspection
   - Recommended robot: quadruped
   - Procedure steps
   - Cottage-specific rationale
   ↓
7. LEARNING UPDATE
   - Record interaction
   - Update user patterns
   - Improve future responses
   ↓
8. MISSION EXECUTION
   - Dynamic task generation
   - Robot assignment
   - Task execution
```

## 🎯 **Key Benefits of Cottage RAG**

### **Contextual Understanding**
- **Zone Awareness**: Knows kitchen layout, landmarks, and connectivity
- **Robot Matching**: Selects appropriate robot based on cottage environment
- **Procedure Knowledge**: Uses cottage-specific procedures and preferences
- **Learning Patterns**: Adapts to user terminology and preferences

### **Scalable Architecture**
- **Multi-Tenant**: Isolated cottage data with shared knowledge
- **Vector Search**: Fast semantic similarity matching
- **Progressive Learning**: Improves with each interaction
- **Resource Efficient**: Optimized storage and caching

The cottage RAG system provides **rich contextual understanding** that transforms simple queries into sophisticated, environment-aware mission plans!
