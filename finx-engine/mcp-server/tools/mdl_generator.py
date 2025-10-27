"""
MDL (Model Definition Language) Generation Tool for MCP
Provides tools to generate MDL files from business requirements
"""

import logging
import json
import os
from typing import Any, Dict, List
from datetime import datetime
from providers.google_ai import GoogleAIProvider
from config import MCPServerConfig


logger = logging.getLogger(__name__)


class MDLGeneratorTool:
    """MCP tool for MDL generation"""
    
    def __init__(self, google_ai_provider: GoogleAIProvider, config: MCPServerConfig):
        """Initialize MDL generator tool"""
        self.ai_provider = google_ai_provider
        self.config = config
        self.output_dir = config.mdl_output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions for MDL generation"""
        return [
            {
                "name": "mdl_generate_from_requirements",
                "description": "Generate MDL (Model Definition Language) from business requirements",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "requirements": {
                            "type": "string",
                            "description": "Business requirements text"
                        },
                        "model_name": {
                            "type": "string",
                            "description": "Name for the generated model"
                        },
                        "include_descriptions": {
                            "type": "boolean",
                            "description": "Include descriptions in MDL (default: true)",
                            "default": True
                        }
                    },
                    "required": ["requirements", "model_name"]
                }
            },
            {
                "name": "mdl_generate_from_schema",
                "description": "Generate MDL from database schema description",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schema_description": {
                            "type": "string",
                            "description": "Database schema description"
                        },
                        "model_name": {
                            "type": "string",
                            "description": "Name for the generated model"
                        },
                        "business_context": {
                            "type": "string",
                            "description": "Optional business context for the schema"
                        }
                    },
                    "required": ["schema_description", "model_name"]
                }
            },
            {
                "name": "mdl_validate_syntax",
                "description": "Validate MDL syntax",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mdl_content": {
                            "type": "string",
                            "description": "MDL content to validate"
                        }
                    },
                    "required": ["mdl_content"]
                }
            }
        ]
    
    def generate_from_requirements(
        self,
        requirements: str,
        model_name: str,
        include_descriptions: bool = True
    ) -> Dict[str, Any]:
        """
        Generate MDL from business requirements
        
        Args:
            requirements: Business requirements text
            model_name: Model name
            include_descriptions: Include descriptions
            
        Returns:
            Generated MDL
        """
        try:
            prompt = f"""Generate a Model Definition Language (MDL) file based on these business requirements:

{requirements}

Model Name: {model_name}

Create a comprehensive MDL that includes:
1. Model definition with name and description
2. Entities/tables with their relationships
3. Attributes/columns with types and descriptions
4. Business rules and constraints
5. Metrics and measures if applicable

Format the output as valid MDL syntax. Include helpful comments explaining the structure."""
            
            mdl_content = self.ai_provider.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4096
            )
            
            # Save MDL to file
            filename = f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mdl"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(mdl_content)
            
            logger.info(f"Generated MDL saved to: {filepath}")
            
            return {
                "success": True,
                "model_name": model_name,
                "mdl_content": mdl_content,
                "filepath": filepath,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating MDL from requirements: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_from_schema(
        self,
        schema_description: str,
        model_name: str,
        business_context: str = None
    ) -> Dict[str, Any]:
        """
        Generate MDL from database schema
        
        Args:
            schema_description: Schema description
            model_name: Model name
            business_context: Optional business context
            
        Returns:
            Generated MDL
        """
        try:
            context_text = f"\nBusiness Context:\n{business_context}" if business_context else ""
            
            prompt = f"""Generate a Model Definition Language (MDL) file from this database schema:

{schema_description}
{context_text}

Model Name: {model_name}

Create MDL that:
1. Maps database tables to MDL entities
2. Maps columns to MDL attributes with appropriate types
3. Defines relationships between entities
4. Includes business-friendly descriptions
5. Specifies any calculated fields or metrics

Output valid MDL syntax with clear documentation."""
            
            mdl_content = self.ai_provider.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4096
            )
            
            # Save MDL to file
            filename = f"{model_name}_schema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mdl"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(mdl_content)
            
            logger.info(f"Generated MDL from schema saved to: {filepath}")
            
            return {
                "success": True,
                "model_name": model_name,
                "mdl_content": mdl_content,
                "filepath": filepath,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating MDL from schema: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_syntax(self, mdl_content: str) -> Dict[str, Any]:
        """
        Validate MDL syntax
        
        Args:
            mdl_content: MDL content to validate
            
        Returns:
            Validation result
        """
        try:
            prompt = f"""Validate this MDL (Model Definition Language) syntax and provide feedback:

{mdl_content}

Check for:
1. Correct MDL syntax
2. Valid entity and attribute definitions
3. Proper relationship definitions
4. Type correctness
5. Any missing required elements

Provide a detailed validation report."""
            
            validation_result = self.ai_provider.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=2048
            )
            
            return {
                "success": True,
                "validation_report": validation_result
            }
            
        except Exception as e:
            logger.error(f"Error validating MDL syntax: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Handle MCP tool calls"""
        try:
            if tool_name == "mdl_generate_from_requirements":
                result = self.generate_from_requirements(**tool_input)
            elif tool_name == "mdl_generate_from_schema":
                result = self.generate_from_schema(**tool_input)
            elif tool_name == "mdl_validate_syntax":
                result = self.validate_syntax(**tool_input)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return json.dumps({"error": str(e)})

