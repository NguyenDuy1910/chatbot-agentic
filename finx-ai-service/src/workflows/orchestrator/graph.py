import logging
from typing import Any, Dict, Type, TypedDict

from langgraph.graph import END

from src.core.base_graph import BaseGraph
from .state import OrchestratorState

logger = logging.getLogger(__name__)


class OrchestratorGraph(BaseGraph):
    """
    Master Orchestrator for complete chatbot workflow.
    
    Workflow:
    1. Initialize Session (load history, context, user preferences)
    2. Intent Classification & Recommendation
       - Classify intent
       - Generate recommendations
    3. Route by Intent:
       - TEXT_TO_SQL -> SQL Processing -> Visualization (if needed)
       - GENERAL -> Data Assistance (streaming)
       - USER_GUIDE -> User Guide Assistance (streaming)
       - MISLEADING_QUERY -> Helpful redirection
    4. Post-Processing (save history, analytics)
    
    User-Friendly Features:
    - Contextual conversation with history
    - Streaming responses for better UX
    - Helpful error messages
    - Smart recommendations
    - Multi-turn conversations
    """
    
    def __init__(self):
        """Initialize the Master Orchestrator Graph."""
        super().__init__("orchestrator")
    
    def get_state_schema(self) -> Type[TypedDict]:
        """Get the state schema for this graph."""
        return OrchestratorState
    
    def _add_nodes(self) -> None:
        """Add all processing nodes to the graph."""
        # Session management
        self.graph.add_node("initialize_session", self._initialize_session_node)
        self.graph.add_node("save_history", self._save_history_node)
        
        # Sub-graph invocation nodes
        self.graph.add_node("intent_recommendation", self._invoke_intent_recommendation)
        self.graph.add_node("sql_processing", self._invoke_sql_processing)
        self.graph.add_node("assistance_visualization", self._invoke_assistance_visualization)
        
        # User experience nodes
        self.graph.add_node("stream_response", self._stream_response_node)
        self.graph.add_node("format_final_response", self._format_final_response_node)
        self.graph.add_node("handle_error", self._handle_error_node)
    
    def _add_edges(self) -> None:
        """Define complete workflow with sub-graph orchestration."""
        
        # ========== Entry Point ==========
        self.graph.set_entry_point("initialize_session")
        
        # ========== Session Initialization ==========
        self.graph.add_edge("initialize_session", "intent_recommendation")
        
        # ========== Intent & Recommendation ==========
        # After intent classification, route based on intent type
        self.graph.add_conditional_edges(
            "intent_recommendation",
            self._route_by_intent,
            {
                "sql_processing": "sql_processing",
                "assistance": "assistance_visualization",
                "error": "handle_error",
            }
        )
        
        # ========== SQL Processing Path ==========
        # After SQL processing, check if visualization is needed
        self.graph.add_conditional_edges(
            "sql_processing",
            self._check_visualization_needed,
            {
                "visualize": "assistance_visualization",
                "finalize": "format_final_response",
            }
        )
        
        # ========== Assistance & Visualization ==========
        # Check if streaming is enabled for this response type
        self.graph.add_conditional_edges(
            "assistance_visualization",
            self._check_streaming,
            {
                "stream": "stream_response",
                "no_stream": "format_final_response",
            }
        )
        
        # ========== Response Formatting ==========
        self.graph.add_edge("stream_response", "format_final_response")
        self.graph.add_edge("format_final_response", "save_history")
        
        # ========== Error Handling ==========
        self.graph.add_edge("handle_error", "save_history")
        
        # ========== Session Cleanup ==========
        self.graph.add_edge("save_history", END)
    
    # ==================== Sub-Graph Invocation Nodes ====================
    
    async def _invoke_intent_recommendation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke Intent & Recommendation sub-graph."""
        logger.info("Invoking Intent & Recommendation Graph...")
        state["current_step"] = "intent_recommendation"
        
        try:
            from src.workflows.intent_recommendation.graph import create_intent_recommendation_graph

            intent_graph = create_intent_recommendation_graph()
            
            # Prepare sub-graph input
            sub_input = {
                "query": state.get("query"),
                "project_id": state.get("project_id"),
                "histories": state.get("conversation_history", []),
                "configuration": state.get("user_preferences", {}),
                "context": state.get("context", {}),
                "instructions": state.get("instructions", []),
                "errors": [],
            }
            
            # Invoke sub-graph
            result = await intent_graph.app.ainvoke(sub_input)
            
            # Merge results back to orchestrator state
            state["intent"] = result.get("intent")
            state["rephrased_question"] = result.get("rephrased_question")
            state["intent_reasoning"] = result.get("intent_reasoning")
            state["confidence_score"] = result.get("confidence_score", 0.0)
            state["recommended_questions"] = result.get("recommended_questions", [])
            state["recommended_relationships"] = result.get("recommended_relationships", [])
            state["db_schemas"] = result.get("db_schemas", [])
            state["retrieved_tables"] = result.get("retrieved_tables", [])
            
            logger.info(f"Intent classified as: {state['intent']}")
            
        except Exception as e:
            logger.error(f"Error in intent recommendation graph: {e}")
            state["errors"].append(f"Intent classification failed: {str(e)}")
            state["intent"] = "ERROR"
        
        return state
    
    async def _invoke_sql_processing(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke SQL Processing sub-graph."""
        logger.info("Invoking SQL Processing Graph...")
        state["current_step"] = "sql_processing"
        
        try:
            from src.workflows.sql_processing.graph import create_sql_processing_graph

            sql_graph = create_sql_processing_graph()
            
            # Detect if follow-up question
            is_followup = self._is_followup_question(state)
            
            # Prepare sub-graph input
            sub_input = {
                "query": state.get("rephrased_question") or state.get("query"),
                "project_id": state.get("project_id"),
                "is_followup": is_followup,
                "previous_sql": state.get("previous_sql"),
                "histories": state.get("conversation_history", []),
                "db_schemas": state.get("db_schemas", []),
                "instructions": state.get("instructions", []),
                "context": state.get("context", {}),
                "max_correction_attempts": 3,
                "errors": [],
            }
            
            # Invoke sub-graph
            result = await sql_graph.app.ainvoke(sub_input)
            
            # Merge results back to orchestrator state
            state["generated_sql"] = result.get("response", {}).get("sql")
            state["sql_reasoning"] = result.get("response", {}).get("reasoning")
            state["sql_answer"] = result.get("response", {}).get("answer")
            state["extracted_tables"] = result.get("response", {}).get("extracted_tables", [])
            state["sql_valid"] = result.get("response", {}).get("is_valid", False)
            state["correction_attempts"] = result.get("response", {}).get("correction_attempts", 0)
            
            # Store for potential follow-up
            state["previous_sql"] = state["generated_sql"]
            
            logger.info(f"SQL generated successfully (valid: {state['sql_valid']})")
            
        except Exception as e:
            logger.error(f"Error in SQL processing graph: {e}")
            state["errors"].append(f"SQL generation failed: {str(e)}")
            state["sql_valid"] = False
        
        return state
    
    async def _invoke_assistance_visualization(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke Assistance & Visualization sub-graph."""
        logger.info("Invoking Assistance & Visualization Graph...")
        state["current_step"] = "assistance_visualization"
        
        try:
            from src.workflows.assistance_visualization.graph import create_assistance_visualization_graph

            assistance_graph = create_assistance_visualization_graph()
            
            # Prepare sub-graph input
            sub_input = {
                "query": state.get("rephrased_question") or state.get("query"),
                "intent": state.get("intent"),
                "project_id": state.get("project_id"),
                "sql_result": state.get("generated_sql"),
                "sql_data": state.get("sql_answer"),
                "db_schemas": state.get("db_schemas", []),
                "context": state.get("context", {}),
                "metadata": {
                    "needs_visualization": state.get("needs_visualization", False),
                    "chart_type": state.get("preferred_chart_type"),
                },
                "adjustment_instructions": state.get("chart_adjustment_instructions"),
                "errors": [],
            }
            
            # Invoke sub-graph
            result = await assistance_graph.app.ainvoke(sub_input)
            
            # Merge results back to orchestrator state
            response = result.get("response", {})
            
            if "assistance" in response:
                state["assistance_response"] = response["assistance"]["response"]
                state["assistance_reasoning"] = response["assistance"]["reasoning"]
            
            if "chart" in response:
                state["chart_schema"] = response["chart"]["schema"]
                state["chart_type"] = response["chart"]["type"]
                state["chart_reasoning"] = response["chart"]["reasoning"]
            
            logger.info("Assistance/Visualization generated successfully")
            
        except Exception as e:
            logger.error(f"Error in assistance/visualization graph: {e}")
            state["errors"].append(f"Assistance/Visualization failed: {str(e)}")
        
        return state
    
    # ==================== Routing Functions ====================
    
    def _route_by_intent(self, state: Dict[str, Any]) -> str:
        """Route to appropriate sub-graph based on intent."""
        intent = state.get("intent")
        
        # Check for errors first
        if intent == "ERROR" or state.get("errors"):
            logger.warning("Routing to error handler")
            return "error"
        
        # Route based on intent
        if intent == "TEXT_TO_SQL":
            logger.info("Routing to SQL Processing")
            return "sql_processing"
        elif intent in ["GENERAL", "USER_GUIDE", "MISLEADING_QUERY"]:
            logger.info("Routing to Assistance & Visualization")
            return "assistance"
        else:
            logger.warning(f"Unknown intent: {intent}, routing to assistance")
            return "assistance"
    
    def _check_visualization_needed(self, state: Dict[str, Any]) -> str:
        """Check if visualization is needed after SQL processing."""
        # Check if SQL was successfully generated
        if not state.get("sql_valid"):
            logger.info("SQL invalid, skipping visualization")
            return "finalize"
        
        # Check user preferences or query content for visualization keywords
        needs_viz = self._should_visualize(state)
        
        if needs_viz:
            logger.info("Visualization needed")
            state["needs_visualization"] = True
            return "visualize"
        else:
            logger.info("No visualization needed")
            return "finalize"
    
    def _check_streaming(self, state: Dict[str, Any]) -> str:
        """Check if streaming is enabled for this response."""
        intent = state.get("intent")
        enable_streaming = state.get("user_preferences", {}).get("enable_streaming", True)
        
        # Stream for GENERAL and USER_GUIDE intents
        should_stream = enable_streaming and intent in ["GENERAL", "USER_GUIDE"]
        
        if should_stream:
            logger.info("Streaming enabled")
            return "stream"
        else:
            logger.info("No streaming")
            return "no_stream"
    
    # ==================== Helper Nodes ====================
    
    async def _initialize_session_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize session with user context and history."""
        logger.info("Initializing session...")
        state["current_step"] = "initialize_session"
        
        try:
            # Load conversation history
            session_id = state.get("session_id")
            if session_id and not state.get("conversation_history"):
                # Load from database or cache
                # state["conversation_history"] = await load_history(session_id)
                state["conversation_history"] = []  # Placeholder
                logger.info(f"Loaded conversation history for session: {session_id}")
            
            # Set defaults
            if "user_preferences" not in state:
                state["user_preferences"] = {
                    "language": "English",
                    "enable_streaming": True,
                    "max_recommendations": 5,
                }
            
            if "errors" not in state:
                state["errors"] = []
            
            # Track start time for analytics
            from datetime import datetime
            state["session_start"] = datetime.utcnow().isoformat()
            
            logger.info("Session initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            state["errors"].append(f"Session initialization failed: {str(e)}")
        
        return state
    
    async def _stream_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Stream response to user for better UX."""
        logger.info("Streaming response...")
        state["current_step"] = "stream_response"
        
        try:
            response_text = state.get("assistance_response", "")
            
            # Simulate streaming (in production, use actual streaming)
            state["streaming_enabled"] = True
            state["stream_chunks"] = self._chunk_text(response_text)
            
            logger.info(f"Streaming {len(state['stream_chunks'])} chunks")
            
        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            state["streaming_enabled"] = False
        
        return state
    
    async def _format_final_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Format final user-friendly response."""
        logger.info("Formatting final response...")
        state["current_step"] = "format_final_response"
        
        try:
            intent = state.get("intent")
            
            # Build comprehensive response
            final_response = {
                "session_id": state.get("session_id"),
                "query": state.get("query"),
                "intent": intent,
                "confidence": state.get("confidence_score", 0.0),
            }
            
            # Add intent-specific content
            if intent == "TEXT_TO_SQL":
                final_response["sql"] = {
                    "query": state.get("generated_sql"),
                    "reasoning": state.get("sql_reasoning"),
                    "answer": state.get("sql_answer"),
                    "tables_used": state.get("extracted_tables", []),
                    "is_valid": state.get("sql_valid", False),
                }
                
                # Add visualization if available
                if state.get("chart_schema"):
                    final_response["visualization"] = {
                        "type": state.get("chart_type"),
                        "schema": state.get("chart_schema"),
                    }
            
            elif intent in ["GENERAL", "USER_GUIDE"]:
                final_response["assistance"] = {
                    "response": state.get("assistance_response"),
                    "reasoning": state.get("assistance_reasoning"),
                }
            
            elif intent == "MISLEADING_QUERY":
                final_response["message"] = "I'm here to help with data analysis. " \
                                          "Could you ask a question related to your data?"
            
            # Add recommendations
            if state.get("recommended_questions"):
                final_response["recommendations"] = {
                    "questions": state.get("recommended_questions"),
                }
            
            if state.get("recommended_relationships"):
                final_response["recommendations"]["relationships"] = state.get("recommended_relationships")
            
            # Add metadata
            final_response["metadata"] = {
                "processing_time": self._calculate_processing_time(state),
                "correction_attempts": state.get("correction_attempts", 0),
                "streaming_enabled": state.get("streaming_enabled", False),
            }
            
            state["final_response"] = final_response
            state["status"] = "success"
            
            logger.info("Final response formatted successfully")
            
        except Exception as e:
            logger.error(f"Error formatting final response: {e}")
            state["errors"].append(f"Response formatting failed: {str(e)}")
            state["status"] = "error"
        
        return state
    
    async def _save_history_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Save conversation to history for multi-turn support."""
        logger.info("Saving conversation history...")
        state["current_step"] = "save_history"
        
        try:
            session_id = state.get("session_id")
            
            if session_id:
                # Prepare history entry
                history_entry = {
                    "query": state.get("query"),
                    "intent": state.get("intent"),
                    "sql": state.get("generated_sql"),
                    "answer": state.get("sql_answer"),
                    "timestamp": state.get("session_start"),
                }
                
                # Add to conversation history
                if "conversation_history" not in state:
                    state["conversation_history"] = []
                
                state["conversation_history"].append(history_entry)
                
                # Save to database (placeholder)
                # await save_history(session_id, history_entry)
                
                logger.info(f"History saved (total: {len(state['conversation_history'])} entries)")
        
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            # Don't fail the entire workflow if history save fails
        
        return state
    
    async def _handle_error_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors gracefully with user-friendly messages."""
        logger.info("Handling error...")
        state["current_step"] = "handle_error"
        
        errors = state.get("errors", [])
        
        # Create user-friendly error message
        if errors:
            error_message = "I encountered an issue while processing your request. "
            
            # Provide helpful suggestions based on error type
            if any("classification" in str(e).lower() for e in errors):
                error_message += "I'm having trouble understanding your question. Could you rephrase it?"
            elif any("sql" in str(e).lower() for e in errors):
                error_message += "I couldn't generate a valid SQL query. Could you provide more details?"
            else:
                error_message += "Please try again or contact support if the issue persists."
            
            state["final_response"] = {
                "status": "error",
                "message": error_message,
                "details": errors if state.get("debug_mode") else None,
                "recommendations": state.get("recommended_questions", []),
            }
        
        logger.warning(f"Error handled: {len(errors)} errors")
        return state
    
    # ==================== Helper Methods ====================
    
    def _is_followup_question(self, state: Dict[str, Any]) -> bool:
        """Detect if current query is a follow-up to previous conversation."""
        history = state.get("conversation_history", [])
        query = state.get("query", "").lower()
        
        # Simple heuristics for follow-up detection
        followup_keywords = ["also", "and", "what about", "how about", "show me more", 
                            "previous", "that", "this", "those", "these"]
        
        has_history = len(history) > 0
        has_followup_keywords = any(keyword in query for keyword in followup_keywords)
        
        return has_history and has_followup_keywords
    
    def _should_visualize(self, state: Dict[str, Any]) -> bool:
        """Determine if visualization is needed based on query and data."""
        query = state.get("query", "").lower()
        
        # Check for visualization keywords
        viz_keywords = ["chart", "graph", "plot", "visualize", "show", "trend", 
                       "distribution", "comparison", "over time"]
        
        has_viz_keywords = any(keyword in query for keyword in viz_keywords)
        
        # Check if SQL result is suitable for visualization (has numeric data)
        # This would be more sophisticated in production
        has_numeric_data = state.get("sql_answer") is not None
        
        return has_viz_keywords or (has_numeric_data and len(state.get("conversation_history", [])) > 0)
    
    def _chunk_text(self, text: str, chunk_size: int = 50) -> list:
        """Split text into chunks for streaming."""
        words = text.split()
        return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    def _calculate_processing_time(self, state: Dict[str, Any]) -> float:
        """Calculate total processing time."""
        from datetime import datetime
        
        start = state.get("session_start")
        if start:
            start_time = datetime.fromisoformat(start)
            end_time = datetime.utcnow()
            return (end_time - start_time).total_seconds()
        
        return 0.0


# Factory function for easy graph creation
def create_orchestrator_graph() -> OrchestratorGraph:
    """
    Create and build the Master Orchestrator graph.
    
    Returns:
        Built OrchestratorGraph ready for execution
    """
    graph = OrchestratorGraph()
    graph.build()
    return graph
