"""
Synchronization Service - Data Synchronization Between Services

This service handles:
- Bidirectional data sync
- Conflict resolution
- Data transformation
- Consistency models
- Progress tracking
- Rollback capabilities
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
import json
from datetime import datetime, timedelta
import uuid
from enum import Enum
import hashlib

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import orjson

logger = logging.getLogger(__name__)


class SyncType(Enum):
    """Types of synchronization"""
    BIDIRECTIONAL = "bidirectional"
    UNIDIRECTIONAL = "unidirectional"
    EVENT_DRIVEN = "event_driven"
    SCHEDULED = "scheduled"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL = "manual"
    MERGE = "merge"
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"


Base = declarative_base()


class SyncRecord(Base):
    """Database model for sync records"""
    __tablename__ = "sync_records"
    
    sync_id = Column(String, primary_key=True)
    sync_type = Column(String, nullable=False)
    source_service = Column(String, nullable=False)
    target_service = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    items_synced = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    conflict_count = Column(Integer, default=0)
    error_message = Column(Text)
    metadata = Column(Text)  # JSON metadata


class DataConflict(Base):
    """Database model for data conflicts"""
    __tablename__ = "data_conflicts"
    
    conflict_id = Column(String, primary_key=True)
    sync_id = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    source_data = Column(Text, nullable=False)  # JSON
    target_data = Column(Text, nullable=False)  # JSON
    conflict_type = Column(String, nullable=False)
    resolution = Column(String)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False)


class SynchronizationService:
    """Service for data synchronization between services"""
    
    def __init__(self):
        """Initialize the synchronization service"""
        logger.info("Initializing Synchronization Service...")
        
        # Configuration
        self.config = {
            "cosmos_db": {
                "endpoint": "your-cosmos-endpoint",
                "key": "your-cosmos-key",
                "database": "warehouse_sync",
                "container": "sync_records"
            },
            "sql_database": {
                "connection_string": "postgresql://user:pass@localhost/warehouse_sync",
                "enabled": True
            },
            "sync_settings": {
                "max_retries": 3,
                "batch_size": 100,
                "timeout": 300,  # 5 minutes
                "conflict_resolution": ConflictResolution.LAST_WRITE_WINS
            }
        }
        
        # Initialize databases
        self.cosmos_client = None
        self.sql_engine = None
        self.sql_session_factory = None
        
        # Active synchronizations
        self.active_syncs = {}
        self.sync_progress = {}
        
        # Data transformers
        self.data_transformers = {}
        self.conflict_resolvers = {}
        
        # Initialize databases
        asyncio.create_task(self._initialize_databases())
        
        # Register default transformers and resolvers
        self._register_default_handlers()
        
        logger.info("Synchronization Service initialized")
    
    async def _initialize_databases(self):
        """Initialize database connections"""
        # Initialize Cosmos DB
        try:
            self.cosmos_client = CosmosClient(
                self.config["cosmos_db"]["endpoint"],
                self.config["cosmos_db"]["key"]
            )
            
            # Create database and container if not exists
            database = self.cosmos_client.get_database_client(
                self.config["cosmos_db"]["database"]
            )
            
            container = database.get_container_client(
                self.config["cosmos_db"]["container"]
            )
            
            # Test connection
            container.query_items(
                query="SELECT TOP 1 * FROM c",
                enable_cross_partition_query=True
            )
            
            logger.info("Cosmos DB initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
        
        # Initialize SQL database
        if self.config["sql_database"]["enabled"]:
            try:
                self.sql_engine = create_engine(
                    self.config["sql_database"]["connection_string"]
                )
                
                # Create tables
                Base.metadata.create_all(self.sql_engine)
                
                # Create session factory
                self.sql_session_factory = sessionmaker(bind=self.sql_engine)
                
                logger.info("SQL database initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize SQL database: {e}")
    
    def _register_default_handlers(self):
        """Register default data transformers and conflict resolvers"""
        
        # Register data transformers
        self.data_transformers.update({
            "warehouse_config": self._transform_warehouse_config,
            "robot_status": self._transform_robot_status,
            "zone_data": self._transform_zone_data,
            "task_info": self._transform_task_info
        })
        
        # Register conflict resolvers
        self.conflict_resolvers.update({
            ConflictResolution.LAST_WRITE_WINS: self._resolve_last_write_wins,
            ConflictResolution.FIRST_WRITE_WINS: self._resolve_first_write_wins,
            ConflictResolution.SOURCE_WINS: self._resolve_source_wins,
            ConflictResolution.TARGET_WINS: self._resolve_target_wins,
            ConflictResolution.MERGE: self._resolve_merge
        })
    
    async def start_synchronization(self, sync_request: Dict) -> str:
        """
        Start data synchronization
        
        Args:
            sync_request: Synchronization request dictionary
            
        Returns:
            Sync ID
        """
        try:
            logger.info(f"Starting synchronization: {sync_request['sync_type']}")
            
            # Generate sync ID
            sync_id = str(uuid.uuid4())
            
            # Create sync record
            sync_record = {
                "sync_id": sync_id,
                "sync_type": sync_request["sync_type"],
                "source_service": sync_request.get("source_service", "unknown"),
                "target_service": sync_request["target_service"],
                "status": "started",
                "started_at": datetime.utcnow().isoformat(),
                "items_synced": 0,
                "items_failed": 0,
                "conflict_count": 0,
                "metadata": json.dumps(sync_request.get("sync_options", {}))
            }
            
            # Save sync record
            await self._save_sync_record(sync_record)
            
            # Start synchronization in background
            sync_task = asyncio.create_task(
                self._execute_synchronization(sync_id, sync_request)
            )
            
            # Track active sync
            self.active_syncs[sync_id] = sync_task
            self.sync_progress[sync_id] = {
                "status": "running",
                "progress": 0,
                "items_processed": 0,
                "total_items": 0,
                "started_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Synchronization started: {sync_id}")
            return sync_id
            
        except Exception as e:
            logger.error(f"Failed to start synchronization: {str(e)}")
            raise
    
    async def _execute_synchronization(self, sync_id: str, sync_request: Dict):
        """Execute the actual synchronization"""
        try:
            sync_type = SyncType(sync_request["sync_type"])
            
            if sync_type == SyncType.BIDIRECTIONAL:
                await self._execute_bidirectional_sync(sync_id, sync_request)
            elif sync_type == SyncType.UNIDIRECTIONAL:
                await self._execute_unidirectional_sync(sync_id, sync_request)
            elif sync_type == SyncType.EVENT_DRIVEN:
                await self._execute_event_driven_sync(sync_id, sync_request)
            elif sync_type == SyncType.SCHEDULED:
                await self._execute_scheduled_sync(sync_id, sync_request)
            else:
                raise ValueError(f"Unsupported sync type: {sync_type}")
            
            # Update sync record
            await self._update_sync_record(sync_id, {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat()
            })
            
            # Update progress
            self.sync_progress[sync_id]["status"] = "completed"
            self.sync_progress[sync_id]["progress"] = 100
            
            logger.info(f"Synchronization completed: {sync_id}")
            
        except Exception as e:
            logger.error(f"Synchronization failed: {sync_id} - {str(e)}")
            
            # Update sync record
            await self._update_sync_record(sync_id, {
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "error_message": str(e)
            })
            
            # Update progress
            self.sync_progress[sync_id]["status"] = "failed"
            self.sync_progress[sync_id]["error"] = str(e)
        
        finally:
            # Clean up active sync
            if sync_id in self.active_syncs:
                del self.active_syncs[sync_id]
    
    async def _execute_unidirectional_sync(self, sync_id: str, sync_request: Dict):
        """Execute unidirectional synchronization"""
        source_service = sync_request["source_service"]
        target_service = sync_request["target_service"]
        source_data = sync_request["source_data"]
        sync_options = sync_request.get("sync_options", {})
        
        # Get data transformer
        entity_type = sync_options.get("entity_type", "default")
        transformer = self.data_transformers.get(entity_type, self._transform_default)
        
        # Transform data
        transformed_data = await transformer(source_data, source_service, target_service)
        
        # Sync to target service
        items_synced = 0
        items_failed = 0
        conflicts = []
        
        for item in transformed_data:
            try:
                # Check for conflicts
                conflict = await self._check_for_conflict(
                    item, target_service, entity_type
                )
                
                if conflict:
                    # Resolve conflict
                    resolution = await self._resolve_conflict(
                        conflict, sync_options.get("conflict_resolution")
                    )
                    conflicts.append(resolution)
                    
                    if resolution["status"] == "resolved":
                        await self._sync_item_to_target(item, target_service)
                        items_synced += 1
                    else:
                        items_failed += 1
                else:
                    # No conflict, sync directly
                    await self._sync_item_to_target(item, target_service)
                    items_synced += 1
                
                # Update progress
                progress = (items_synced + items_failed) / len(transformed_data) * 100
                self.sync_progress[sync_id]["progress"] = progress
                self.sync_progress[sync_id]["items_processed"] = items_synced + items_failed
                
            except Exception as e:
                logger.error(f"Failed to sync item: {str(e)}")
                items_failed += 1
        
        # Update sync record
        await self._update_sync_record(sync_id, {
            "items_synced": items_synced,
            "items_failed": items_failed,
            "conflict_count": len(conflicts)
        })
    
    async def _execute_bidirectional_sync(self, sync_id: str, sync_request: Dict):
        """Execute bidirectional synchronization"""
        # This would implement two-way sync logic
        # For now, delegate to unidirectional sync in both directions
        
        # Sync from source to target
        await self._execute_unidirectional_sync(sync_id, sync_request)
        
        # Sync from target to source (reverse)
        reverse_request = sync_request.copy()
        reverse_request["source_service"] = sync_request["target_service"]
        reverse_request["target_service"] = sync_request["source_service"]
        
        # Get target data
        target_data = await self._get_service_data(
            sync_request["target_service"], 
            sync_request.get("sync_options", {})
        )
        reverse_request["source_data"] = target_data
        
        await self._execute_unidirectional_sync(sync_id, reverse_request)
    
    async def _execute_event_driven_sync(self, sync_id: str, sync_request: Dict):
        """Execute event-driven synchronization"""
        # This would listen to events and sync accordingly
        # For now, implement as a scheduled sync
        await self._execute_scheduled_sync(sync_id, sync_request)
    
    async def _execute_scheduled_sync(self, sync_id: str, sync_request: Dict):
        """Execute scheduled synchronization"""
        # This would run on a schedule
        # For now, implement as unidirectional sync
        await self._execute_unidirectional_sync(sync_id, sync_request)
    
    async def _check_for_conflict(self, item: Dict, target_service: str, entity_type: str) -> Optional[Dict]:
        """Check if item conflicts with target service data"""
        try:
            # Get existing item from target service
            entity_id = item.get("id") or item.get("entity_id")
            if not entity_id:
                return None
            
            existing_item = await self._get_item_from_service(
                entity_id, target_service, entity_type
            )
            
            if not existing_item:
                return None  # No conflict if item doesn't exist
            
            # Compare data
            source_hash = self._calculate_data_hash(item)
            target_hash = self._calculate_data_hash(existing_item)
            
            if source_hash == target_hash:
                return None  # No conflict if data is identical
            
            # Conflict detected
            return {
                "conflict_id": str(uuid.uuid4()),
                "entity_id": entity_id,
                "entity_type": entity_type,
                "source_data": item,
                "target_data": existing_item,
                "conflict_type": "data_mismatch",
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Conflict check failed: {str(e)}")
            return None
    
    async def _resolve_conflict(self, conflict: Dict, resolution_strategy: ConflictResolution) -> Dict:
        """Resolve data conflict"""
        try:
            strategy = resolution_strategy or self.config["sync_settings"]["conflict_resolution"]
            resolver = self.conflict_resolvers.get(strategy)
            
            if not resolver:
                raise ValueError(f"Unknown conflict resolution strategy: {strategy}")
            
            resolution = await resolver(conflict)
            
            # Save conflict record
            await self._save_conflict_record(conflict, resolution)
            
            return resolution
            
        except Exception as e:
            logger.error(f"Conflict resolution failed: {str(e)}")
            return {
                "conflict_id": conflict["conflict_id"],
                "status": "failed",
                "error": str(e)
            }
    
    async def _resolve_last_write_wins(self, conflict: Dict) -> Dict:
        """Resolve conflict by keeping last write"""
        source_time = conflict["source_data"].get("updated_at", "")
        target_time = conflict["target_data"].get("updated_at", "")
        
        if source_time > target_time:
            winner = "source"
            winning_data = conflict["source_data"]
        else:
            winner = "target"
            winning_data = conflict["target_data"]
        
        return {
            "conflict_id": conflict["conflict_id"],
            "resolution": ConflictResolution.LAST_WRITE_WINS.value,
            "winner": winner,
            "winning_data": winning_data,
            "status": "resolved"
        }
    
    async def _resolve_first_write_wins(self, conflict: Dict) -> Dict:
        """Resolve conflict by keeping first write"""
        source_time = conflict["source_data"].get("created_at", "")
        target_time = conflict["target_data"].get("created_at", "")
        
        if source_time < target_time:
            winner = "source"
            winning_data = conflict["source_data"]
        else:
            winner = "target"
            winning_data = conflict["target_data"]
        
        return {
            "conflict_id": conflict["conflict_id"],
            "resolution": ConflictResolution.FIRST_WRITE_WINS.value,
            "winner": winner,
            "winning_data": winning_data,
            "status": "resolved"
        }
    
    async def _resolve_source_wins(self, conflict: Dict) -> Dict:
        """Resolve conflict by keeping source data"""
        return {
            "conflict_id": conflict["conflict_id"],
            "resolution": ConflictResolution.SOURCE_WINS.value,
            "winner": "source",
            "winning_data": conflict["source_data"],
            "status": "resolved"
        }
    
    async def _resolve_target_wins(self, conflict: Dict) -> Dict:
        """Resolve conflict by keeping target data"""
        return {
            "conflict_id": conflict["conflict_id"],
            "resolution": ConflictResolution.TARGET_WINS.value,
            "winner": "target",
            "winning_data": conflict["target_data"],
            "status": "resolved"
        }
    
    async def _resolve_merge(self, conflict: Dict) -> Dict:
        """Resolve conflict by merging data"""
        try:
            source_data = conflict["source_data"]
            target_data = conflict["target_data"]
            
            # Simple merge strategy - combine non-conflicting fields
            merged_data = {}
            
            # Add all fields from source
            for key, value in source_data.items():
                if key not in ["id", "entity_id", "created_at", "updated_at"]:
                    merged_data[key] = value
            
            # Add fields from target that don't exist in source
            for key, value in target_data.items():
                if key not in merged_data and key not in ["id", "entity_id", "created_at", "updated_at"]:
                    merged_data[key] = value
            
            # Keep metadata from source
            merged_data["id"] = source_data.get("id", target_data.get("id"))
            merged_data["entity_id"] = conflict["entity_id"]
            merged_data["created_at"] = min(
                source_data.get("created_at", ""),
                target_data.get("created_at", "")
            )
            merged_data["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "conflict_id": conflict["conflict_id"],
                "resolution": ConflictResolution.MERGE.value,
                "winner": "merged",
                "winning_data": merged_data,
                "status": "resolved"
            }
            
        except Exception as e:
            logger.error(f"Merge resolution failed: {str(e)}")
            return {
                "conflict_id": conflict["conflict_id"],
                "resolution": ConflictResolution.MERGE.value,
                "status": "failed",
                "error": str(e)
            }
    
    def _calculate_data_hash(self, data: Dict) -> str:
        """Calculate hash of data for comparison"""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    async def _sync_item_to_target(self, item: Dict, target_service: str):
        """Sync item to target service"""
        # This would make HTTP request to target service
        # For now, just log the operation
        logger.info(f"Syncing item to {target_service}: {item.get('id', 'unknown')}")
    
    async def _get_item_from_service(self, entity_id: str, service: str, entity_type: str) -> Optional[Dict]:
        """Get item from service"""
        # This would make HTTP request to get item
        # For now, return None (no existing item)
        return None
    
    async def _get_service_data(self, service: str, options: Dict) -> List[Dict]:
        """Get data from service"""
        # This would make HTTP request to get data
        # For now, return empty list
        return []
    
    # Data transformers
    async def _transform_warehouse_config(self, data: Dict, source: str, target: str) -> List[Dict]:
        """Transform warehouse configuration data"""
        return [data]  # Simple pass-through
    
    async def _transform_robot_status(self, data: Dict, source: str, target: str) -> List[Dict]:
        """Transform robot status data"""
        return [data]  # Simple pass-through
    
    async def _transform_zone_data(self, data: Dict, source: str, target: str) -> List[Dict]:
        """Transform zone data"""
        return [data]  # Simple pass-through
    
    async def _transform_task_info(self, data: Dict, source: str, target: str) -> List[Dict]:
        """Transform task information"""
        return [data]  # Simple pass-through
    
    async def _transform_default(self, data: Dict, source: str, target: str) -> List[Dict]:
        """Default data transformer"""
        return [data]  # Simple pass-through
    
    async def get_sync_status(self, sync_id: str) -> Dict:
        """Get synchronization status"""
        if sync_id in self.sync_progress:
            return self.sync_progress[sync_id]
        
        # Get from database
        sync_record = await self._get_sync_record(sync_id)
        if sync_record:
            return {
                "status": sync_record["status"],
                "progress": 100 if sync_record["status"] == "completed" else 0,
                "items_synced": sync_record["items_synced"],
                "items_failed": sync_record["items_failed"],
                "conflict_count": sync_record["conflict_count"],
                "started_at": sync_record["started_at"],
                "completed_at": sync_record.get("completed_at")
            }
        
        return {"error": "Sync not found"}
    
    async def monitor_synchronization_progress(self, sync_id: str):
        """Monitor synchronization progress"""
        while sync_id in self.active_syncs:
            try:
                # Update progress
                progress = self.sync_progress.get(sync_id, {})
                
                # Log progress
                if progress.get("status") == "running":
                    logger.info(f"Sync progress {sync_id}: {progress.get('progress', 0):.1f}%")
                
                # Check if completed
                if progress.get("status") in ["completed", "failed"]:
                    break
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Progress monitoring error: {str(e)}")
                break
    
    async def _save_sync_record(self, sync_record: Dict):
        """Save sync record to database"""
        try:
            if self.cosmos_client:
                container = self.cosmos_client.get_database_client(
                    self.config["cosmos_db"]["database"]
                ).get_container_client(
                    self.config["cosmos_db"]["container"]
                )
                
                container.upsert_item(sync_record)
            
            if self.sql_session_factory:
                session = self.sql_session_factory()
                try:
                    record = SyncRecord(
                        sync_id=sync_record["sync_id"],
                        sync_type=sync_record["sync_type"],
                        source_service=sync_record["source_service"],
                        target_service=sync_record["target_service"],
                        status=sync_record["status"],
                        started_at=datetime.fromisoformat(sync_record["started_at"]),
                        completed_at=datetime.fromisoformat(sync_record["completed_at"]) if sync_record.get("completed_at") else None,
                        items_synced=sync_record["items_synced"],
                        items_failed=sync_record["items_failed"],
                        conflict_count=sync_record["conflict_count"],
                        error_message=sync_record.get("error_message"),
                        metadata=sync_record.get("metadata")
                    )
                    
                    session.merge(record)
                    session.commit()
                    
                finally:
                    session.close()
                    
        except Exception as e:
            logger.error(f"Failed to save sync record: {str(e)}")
    
    async def _update_sync_record(self, sync_id: str, updates: Dict):
        """Update sync record"""
        try:
            if self.cosmos_client:
                container = self.cosmos_client.get_database_client(
                    self.config["cosmos_db"]["database"]
                ).get_container_client(
                    self.config["cosmos_db"]["container"]
                )
                
                # Get existing record
                existing = container.read_item(
                    item=sync_id,
                    partition_key=sync_id
                )
                
                # Update fields
                for key, value in updates.items():
                    existing[key] = value
                
                container.upsert_item(existing)
            
            if self.sql_session_factory:
                session = self.sql_session_factory()
                try:
                    record = session.query(SyncRecord).filter(
                        SyncRecord.sync_id == sync_id
                    ).first()
                    
                    if record:
                        for key, value in updates.items():
                            if hasattr(record, key):
                                if key in ["started_at", "completed_at"] and value:
                                    setattr(record, key, datetime.fromisoformat(value))
                                else:
                                    setattr(record, key, value)
                        
                        session.commit()
                    
                finally:
                    session.close()
                    
        except Exception as e:
            logger.error(f"Failed to update sync record: {str(e)}")
    
    async def _get_sync_record(self, sync_id: str) -> Optional[Dict]:
        """Get sync record from database"""
        try:
            if self.cosmos_client:
                container = self.cosmos_client.get_database_client(
                    self.config["cosmos_db"]["database"]
                ).get_container_client(
                    self.config["cosmos_db"]["container"]
                )
                
                return container.read_item(
                    item=sync_id,
                    partition_key=sync_id
                )
            
            if self.sql_session_factory:
                session = self.sql_session_factory()
                try:
                    record = session.query(SyncRecord).filter(
                        SyncRecord.sync_id == sync_id
                    ).first()
                    
                    if record:
                        return {
                            "sync_id": record.sync_id,
                            "sync_type": record.sync_type,
                            "source_service": record.source_service,
                            "target_service": record.target_service,
                            "status": record.status,
                            "started_at": record.started_at.isoformat(),
                            "completed_at": record.completed_at.isoformat() if record.completed_at else None,
                            "items_synced": record.items_synced,
                            "items_failed": record.items_failed,
                            "conflict_count": record.conflict_count,
                            "error_message": record.error_message,
                            "metadata": record.metadata
                        }
                    
                finally:
                    session.close()
                    
        except Exception as e:
            logger.error(f"Failed to get sync record: {str(e)}")
        
        return None
    
    async def _save_conflict_record(self, conflict: Dict, resolution: Dict):
        """Save conflict record to database"""
        try:
            if self.sql_session_factory:
                session = self.sql_session_factory()
                try:
                    record = DataConflict(
                        conflict_id=conflict["conflict_id"],
                        sync_id=conflict.get("sync_id", ""),
                        entity_id=conflict["entity_id"],
                        entity_type=conflict["entity_type"],
                        source_data=json.dumps(conflict["source_data"]),
                        target_data=json.dumps(conflict["target_data"]),
                        conflict_type=conflict["conflict_type"],
                        resolution=resolution.get("resolution"),
                        resolved_at=datetime.fromisoformat(resolution.get("resolved_at", datetime.utcnow().isoformat())) if resolution.get("resolved_at") else None,
                        created_at=datetime.fromisoformat(conflict["created_at"])
                    )
                    
                    session.merge(record)
                    session.commit()
                    
                finally:
                    session.close()
                    
        except Exception as e:
            logger.error(f"Failed to save conflict record: {str(e)}")
    
    async def check_database_health(self) -> str:
        """Check database connectivity"""
        try:
            # Check Cosmos DB
            if self.cosmos_client:
                database = self.cosmos_client.get_database_client(
                    self.config["cosmos_db"]["database"]
                )
                container = database.get_container_client(
                    self.config["cosmos_db"]["container"]
                )
                
                # Test query
                list(container.query_items(
                    query="SELECT TOP 1 * FROM c",
                    enable_cross_partition_query=True
                ))
            
            # Check SQL database
            if self.sql_session_factory:
                session = self.sql_session_factory()
                try:
                    session.execute("SELECT 1")
                    session.commit()
                finally:
                    session.close()
            
            return "healthy"
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return "unhealthy"
