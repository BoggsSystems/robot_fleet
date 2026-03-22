"""
Integration of Contextual Intent Service with Mission Brain

This module shows how to integrate the contextual AI system into the existing
mission planning pipeline.
"""

from .contextual_intent import ContextualIntentService, ContextualMemory
from .local import LocalIntentService


def create_contextual_mission_brain(backend, use_contextual_ai: bool = True):
    """Create a mission brain with contextual AI capabilities."""
    
    # Get known zones from backend
    site_graph = backend.get_site_graph()
    known_zones = [zone.zone_id for zone in backend.list_zones()]
    
    # Create fallback local intent service
    fallback_service = LocalIntentService(known_zones)
    
    # Create contextual memory system
    memory = ContextualMemory()
    
    # Create enhanced intent service
    if use_contextual_ai:
        intent_service = ContextualIntentService(
            known_zones=known_zones,
            fallback=fallback_service,
            memory=memory
        )
    else:
        intent_service = fallback_service
    
    # Import and create LocalMissionBrain with enhanced intent service
    from .local import (
        LocalMissionBrain,
        LocalPolicyEngine,
        LocalProposalService,
        LocalResourceAssessmentService,
        LocalMissionPlanner,
        LocalAssignmentEngine,
        LocalValidatedPlanService,
        LocalExplanationService
    )
    
    # Create all services
    policy_engine = LocalPolicyEngine()
    proposal_service = LocalProposalService(backend)
    resource_assessment = LocalResourceAssessmentService(backend)
    mission_planner = LocalMissionPlanner()
    assignment_engine = LocalAssignmentEngine()
    validation_service = LocalValidatedPlanService(backend)
    explanation_service = LocalExplanationService()
    
    # Create mission brain with contextual intent service
    brain = LocalMissionBrain(
        intent=intent_service,
        policy=policy_engine,
        proposal=proposal_service,
        resources=resource_assessment,
        planner=mission_planner,
        assigner=assignment_engine,
        validator=validation_service,
        explainer=explanation_service,
        backend=backend
    )
    
    # Store memory reference for feedback learning
    brain._contextual_memory = memory
    
    return brain


class ContextualMissionBrain:
    """Enhanced mission brain with contextual learning."""
    
    def __init__(self, backend, use_contextual_ai: bool = True):
        self._brain = create_contextual_mission_brain(backend, use_contextual_ai)
        self._contextual_memory = getattr(self._brain, '_contextual_memory', None)
    
    def preview_mission(self, request_text: str, *, requested_by: str, context: dict = None) -> dict:
        """Preview mission with contextual understanding."""
        result = self._brain.preview_mission(request_text, requested_by=requested_by, context=context)
        
        # Add contextual insights to result
        if self._contextual_memory:
            result["contextual_insights"] = {
                "memory_summary": self._contextual_memory.get_memory_summary(),
                "learned_patterns": self._contextual_memory._memory["learned_patterns"],
                "adaptations": self._contextual_memory._memory["adaptations"]
            }
        
        return result
    
    def learn_from_mission(self, mission_id: str, execution_result: dict) -> None:
        """Learn from mission execution results."""
        if self._contextual_memory and hasattr(self._brain._intent, 'learn_from_feedback'):
            self._brain._intent.learn_from_feedback(mission_id, execution_result)
    
    def add_user_knowledge(self, user_id: str, knowledge: dict) -> None:
        """Add user-specific knowledge to memory."""
        if self._contextual_memory:
            # Add zone aliases
            if "zone_aliases" in knowledge:
                for alias, actual_zone in knowledge["zone_aliases"].items():
                    self._contextual_memory.add_zone_alias(alias, actual_zone)
            
            # Add task shortcuts
            if "task_shortcuts" in knowledge:
                for shortcut, full_task in knowledge["task_shortcuts"].items():
                    self._contextual_memory.add_task_shortcut(shortcut, full_task)
    
    def get_contextual_summary(self) -> dict:
        """Get summary of contextual learning."""
        if self._contextual_memory:
            return self._contextual_memory.get_memory_summary()
        return {"message": "Contextual learning not enabled"}


# Example usage and integration points
def example_contextual_usage():
    """Example of how to use the contextual mission brain."""
    
    # Import backend services
    from fleet_control.services import FleetBackendServices
    from fleet_control.config import LocalRuntimeConfig
    
    # Create backend
    backend = FleetBackendServices(
        store=ShadowWorldStore(),
        config=LocalRuntimeConfig()
    )
    backend.ensure_defaults()
    
    # Create contextual mission brain
    brain = ContextualMissionBrain(backend, use_contextual_ai=True)
    
    # Example requests showing learning progression
    
    # First interaction - AI learns basic cottage layout
    result1 = brain.preview_mission(
        request_text="Check the kitchen for groceries and bring them to the living room",
        requested_by="user@home"
    )
    
    # Second interaction - AI uses learned context
    result2 = brain.preview_mission(
        request_text="Scan the kitchen area",  # AI knows "kitchen" from previous interaction
        requested_by="user@home"
    )
    
    # Third interaction - AI learns user terminology
    result3 = brain.preview_mission(
        request_text="Do a quick tidy in the living room",  # AI learns "quick tidy" = light cleaning
        requested_by="user@home"
    )
    
    # Add user-specific knowledge
    brain.add_user_knowledge("user@home", {
        "zone_aliases": {
            "pantry": "kitchen",
            "den": "living_room"
        },
        "task_shortcuts": {
            "quick tidy": "light_cleaning_and_organization",
            "stock check": "inventory_inspection"
        }
    })
    
    # Fourth interaction - AI uses learned aliases and shortcuts
    result4 = brain.preview_mission(
        request_text="Do a stock check in the pantry",  # AI translates to inventory in kitchen
        requested_by="user@home"
    )
    
    # Learn from execution results
    brain.learn_from_mission("msn-123", {
        "success": True,
        "execution_time": 12.5,
        "robot_used": "r1_kitchen_bot",
        "user_satisfaction": "high"
    })
    
    # Get contextual summary
    summary = brain.get_contextual_summary()
    print(f"Learned {summary['total_interactions']} interactions")
    print(f"User terms learned: {summary['user_terms']}")
    
    return brain, [result1, result2, result3, result4, summary]


# Integration with existing server
def integrate_contextual_brain():
    """Example of integrating contextual brain with existing server."""
    
    # In server.py, replace the existing mission brain initialization:
    
    """
    # Replace this:
    _mission_brain = LocalMissionBrain(
        intent=OpenAIIntentService(known_zones, LocalIntentService(known_zones)),
        policy=LocalPolicyEngine(),
        proposal=LocalProposalService(_backend_services),
        resources=LocalResourceAssessmentService(_backend_services),
        planner=LocalMissionPlanner(),
        assigner=LocalAssignmentEngine(),
        validator=LocalValidatedPlanService(_backend_services),
        explainer=LocalExplanationService(),
        backend=_backend_services
    )
    
    # With this:
    _mission_brain = ContextualMissionBrain(_backend_services, use_contextual_ai=True)._brain
    """
    
    pass


if __name__ == "__main__":
    # Run example
    brain, results = example_contextual_usage()
    print("Contextual AI system demonstration complete!")
