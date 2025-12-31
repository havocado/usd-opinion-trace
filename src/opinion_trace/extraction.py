"""
USD opinion extraction - pure data gathering.

Queries USD stage and builds structured opinion data with no analysis.
Enables reuse without diagnosis dependency.
"""

import os
from dataclasses import dataclass
from typing import Any

from pxr import Usd, Sdf, Pcp


@dataclass
class OpinionInfo:
    """Information about a single opinion in the property stack."""
    index: int
    layer_identifier: str
    layer_name: str          # basename for display
    arc_type: str            # "Local", "Reference", etc.
    is_direct: bool          # vs ancestral
    value: Any
    has_timesamples: bool
    is_blocked: bool         # Sdf.ValueBlock


@dataclass
class ExtractionResult:
    """Complete extraction data for an attribute opinion stack."""
    stage_path: str
    prim_path: str
    attr_name: str
    time_code: float | None
    resolved_value: Any
    resolved_value_type: str
    opinions: list[OpinionInfo]
    layer_muting: dict[str, bool]   # layer_id → is_muted
    prim_is_loaded: bool
    error: dict | None              # {"code": ..., "message": ...}


def extract_opinions(
    stage_path: str, 
    prim_path: str, 
    attr_name: str, 
    time: float | None = None
) -> ExtractionResult:
    """
    Extract all opinions for an attribute. Pure data gathering.
    No analysis of which opinion wins or why.
    
    Args:
        stage_path: Path to USD stage file
        prim_path: Path to prim (e.g., "/World/Chair/Mesh")
        attr_name: Attribute name (e.g., "xformOp:translate")
        time: Optional time code for time-sampled data
        
    Returns:
        ExtractionResult with all opinion data or error information
    """
    # 1. Open stage
    stage = Usd.Stage.Open(stage_path)
    if not stage:
        return _create_error_result(
            stage_path, prim_path, attr_name, time,
            "STAGE_NOT_FOUND",
            f"Could not open stage '{stage_path}'"
        )
    
    # 2. Get prim
    prim = stage.GetPrimAtPath(prim_path)
    if not prim or not prim.IsValid():
        return _create_error_result(
            stage_path, prim_path, attr_name, time,
            "PRIM_NOT_FOUND",
            f"Prim '{prim_path}' does not exist"
        )
    
    # 3. Get attribute
    attr = prim.GetAttribute(attr_name)
    if not attr:
        return _create_error_result(
            stage_path, prim_path, attr_name, time,
            "ATTR_NOT_FOUND",
            f"Attribute '{attr_name}' does not exist on prim"
        )
    
    # 4. Get resolved value
    time_code = Usd.TimeCode(time) if time is not None else Usd.TimeCode.Default()
    resolved_value = attr.Get(time_code)
    
    # 5. Get property stack
    prop_stack = attr.GetPropertyStack(time_code)
    
    # 6. Build opinion list
    opinions = []
    for i, spec in enumerate(prop_stack):
        arc_type = get_arc_type_for_spec(prim, spec)
        is_direct = is_spec_direct(prim, spec)
        
        # Get value - check for block
        value = spec.default
        is_blocked = isinstance(value, type(Sdf.ValueBlock()))
        
        # Check for timesamples
        has_timesamples = spec.HasInfo('timeSamples')
        
        opinions.append(OpinionInfo(
            index=i,
            layer_identifier=spec.layer.identifier,
            layer_name=os.path.basename(spec.layer.identifier),
            arc_type=arc_type,
            is_direct=is_direct,
            value=value,
            has_timesamples=has_timesamples,
            is_blocked=is_blocked,
        ))
    
    # 7. Gather layer states (for diagnosis to use)
    all_layers = {o.layer_identifier for o in opinions}
    layer_muting = {lid: stage.IsLayerMuted(lid) for lid in all_layers}

    # 8. Throw error if: only 1 opinion found, but its value is null/blocked
    if len(opinions) == 1 and (resolved_value is None or isinstance(resolved_value, type(Sdf.ValueBlock()))):
        return _create_error_result(
            stage_path, prim_path, attr_name, time,
            "NO_VALID_OPINIONS",
            f"Attribute '{attr_name}' has no valid opinions (only one opinion found which is null or blocked)"
        )
    
    return ExtractionResult(
        stage_path=stage_path,
        prim_path=prim_path,
        attr_name=attr_name,
        time_code=time,
        resolved_value=resolved_value,
        resolved_value_type=get_value_type_name(resolved_value),
        opinions=opinions,
        layer_muting=layer_muting,
        prim_is_loaded=prim.IsLoaded(),
        error=None,
    )


def get_arc_type_for_spec(prim: Usd.Prim, spec: Sdf.PropertySpec) -> str:
    """
    Get the arc type that brings this property spec into the composed prim.
    """
    prim_index = prim.GetPrimIndex()
    
    # Get the prim path for this property spec
    # Note: GetPrimPath() will mistake variants as locals, so use GetPrimOrPrimVariantSelectionPath instead
    prim_path = spec.path.GetPrimOrPrimVariantSelectionPath()
    layer = spec.layer
    
    # Use USD's built-in method to find the exact node
    node = prim_index.GetNodeProvidingSpec(layer, prim_path)
    
    if node:
        return arc_type_to_string(node.arcType)
    
    return "Local"  # Fallback


def is_spec_direct(prim: Usd.Prim, spec: Sdf.PropertySpec) -> bool:
    """
    Check if arc introducing this spec is direct (not ancestral).
    
    Direct arcs are authored directly on the prim, while ancestral arcs
    are inherited from ancestor prims.
    
    Args:
        prim: USD prim
        spec: Property spec to check
        
    Returns:
        True if arc is direct, False if ancestral
    """
    # Use composition query to check arc ancestry
    query = Usd.PrimCompositionQuery(prim)
    layer = spec.layer
    
    for arc in query.GetCompositionArcs():
        # Check if this arc introduces our layer
        arc_layer = arc.GetIntroducingLayer()
        if arc_layer and arc_layer.identifier == layer.identifier:
            # Check if ancestral
            return not arc.IsAncestral()
    
    # Default to True (direct) for local layers
    return True


def arc_type_to_string(arc_type: Pcp.ArcType) -> str:
    """
    Convert Pcp.ArcType enum to human-readable string.
    
    Args:
        arc_type: Pcp.ArcType enum value
        
    Returns:
        String like "Local", "Reference", "Payload"
    """
    arc_map = {
        Pcp.ArcTypeRoot: "Local",
        Pcp.ArcTypeInherit: "Inherit",
        Pcp.ArcTypeVariant: "Variant",
        Pcp.ArcTypeReference: "Reference",
        Pcp.ArcTypePayload: "Payload",
        Pcp.ArcTypeSpecialize: "Specialize",
    }
    
    # Handle Relocate (may not exist in older USD versions)
    if hasattr(Pcp, 'ArcTypeRelocate'):
        arc_map[Pcp.ArcTypeRelocate] = "Relocate"
    
    return arc_map.get(arc_type, "Unknown")


def get_value_type_name(value: Any) -> str:
    """
    Get USD type name for resolved value.
    
    Args:
        value: Resolved attribute value
        
    Returns:
        Type name string (e.g., 'GfVec3d', 'float', 'str')
    """
    if value is None:
        return "None"
    
    type_name = type(value).__name__
    
    # Handle USD types nicely
    if hasattr(value, '__class__') and hasattr(value.__class__, '__module__'):
        module = value.__class__.__module__
        if module and module.startswith('pxr.'):
            # Return just the type name for USD types
            return type_name
    
    return type_name


def _create_error_result(
    stage_path: str,
    prim_path: str,
    attr_name: str,
    time: float | None,
    error_code: str,
    error_message: str
) -> ExtractionResult:
    """
    Create an ExtractionResult with error information.
    
    Args:
        stage_path: Stage path (for result context)
        prim_path: Prim path (for result context)
        attr_name: Attribute name (for result context)
        time: Time code (for result context)
        error_code: Error code string
        error_message: Human-readable error message
        
    Returns:
        ExtractionResult with error populated
    """
    return ExtractionResult(
        stage_path=stage_path,
        prim_path=prim_path,
        attr_name=attr_name,
        time_code=time,
        resolved_value=None,
        resolved_value_type="None",
        opinions=[],
        layer_muting={},
        prim_is_loaded=False,
        error={"code": error_code, "message": error_message}
    )
