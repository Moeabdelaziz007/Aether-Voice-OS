from __future__ import annotations

import logging

import jsonschema
from google.genai import types
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class OpenClaw(BaseModel):
    """Open a specialized tool interface."""
    tool_id: str = Field(..., description="The ID of the tool to open")

class SoulSwap(BaseModel):
    """Swap the active soul/expert."""
    target_soul: str = Field(..., description="Target soul name")

class DiagnoseStructure(BaseModel):
    """Diagnose the current system structure."""
    component: str = Field(..., description="The component to diagnose")

class ForgeAgentManifest(BaseModel):
    """Extract structured agent configuration from the user's vocal description and environmental context for the Aether Forge protocol V2.0."""
    name: str = Field(..., description="The name of the AI consciousness.")
    role: str = Field(..., description="The core professional role or persona of the agent (e.g., Senior Systems Architect).")
    skills: list[str] = Field(default_factory=list, description="Specific technical or creative skills (e.g., Kubernetes, Rust, Design Theory).")
    tone: str = Field(default="Analytical", description="The vocal and behavioral tone (e.g., Analytical, Mentor, Sarcastic).")
    personality_quarks: list[str] = Field(default_factory=list, description="Subtle character traits or quirks (e.g., 'obsessed with clean code', 'loves sci-fi metaphors').")
    visual_grounding: str = Field(default="", description="Context captured from user's screen that influenced the design (e.g., 'Detected Next.js project open').")

class ToggleHUD(BaseModel):
    """Toggle the visibility of the SRE Telemetry HUD or other interface elements."""
    element: str = Field(..., description="The UI element to toggle (e.g., 'telemetry', 'omnibar', 'all')")
    visible: bool = Field(..., description="Whether the element should be visible or hidden")

# Late import for VisualDiagnoseInput to avoid circularity if possible
from core.ai.tools.visual_diagnose import VisualDiagnoseInput


class ToolRegistry:
    """Typed registry for declarative tools with response_schema enforcement."""
    def __init__(self):
        self.tools = {
            "open_claw": OpenClaw,
            "soul_swap": SoulSwap,
            "diagnose_structure": DiagnoseStructure,
            "visual_diagnose": VisualDiagnoseInput,
            "forge_agent_manifest": ForgeAgentManifest,
            "toggle_hud": ToggleHUD
        }

    def get_declarations(self) -> list[types.FunctionDeclaration]:
        declarations = []
        for name, model in self.tools.items():
            schema = model.model_json_schema()
            # Enforce basic jsonschema validation strictly before sending to Gemini
            jsonschema.Draft202012Validator.check_schema(schema)
            declarations.append(
                types.FunctionDeclaration(
                    name=name,
                    description=model.__doc__ or "",
                    parameters=schema,
                    response_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "message": {"type": "string"}}, "required": ["success"]}
                )
            )
        return declarations

    def validate(self, name: str, args: dict) -> bool:
        """Validate tool call arguments against the registered Pydantic model."""
        if name not in self.tools:
            return True # Not managed by this registry (fallback to router)
        
        try:
            model = self.tools[name]
            # Use jsonschema validator for strict primitive check
            jsonschema.validate(instance=args, schema=model.model_json_schema())
            # Then use pydantic for deep typing
            model(**args)
            return True
        except Exception as e:
            logger.error("⚡ Tool Validation Error [%s]: %s", name, e)
            return False
