"""
Reason codes for USD opinion composition diagnosis.

Each code maps to a detailed explanation and actionable suggestions.
Organized by category: arc types, secondary ordering, layer states, blocks, edge cases.
"""

REASON_CODES = {
    # =========================================================================
    # ARC TYPE COMPARISONS - LIVRPS hierarchy
    # =========================================================================
    
    # Local over everything
    "arc_type_local_over_inherit": {
        "detail": "Local arc (sublayer) is stronger than Inherit arc",
        "suggestions": ["Author opinion in a Local/sublayer layer", "Move to stronger position in sublayer stack"]
    },
    "arc_type_local_over_variant": {
        "detail": "Local arc (sublayer) is stronger than Variant arc",
        "suggestions": ["Author opinion directly in local layer, not within variant", "Promote opinion out of variant"]
    },
    "arc_type_local_over_reference": {
        "detail": "Local arc (sublayer) is stronger than Reference arc",
        "suggestions": ["Author opinion in the referencing layer", "Move to local sublayer stack"]
    },
    "arc_type_local_over_payload": {
        "detail": "Local arc (sublayer) is stronger than Payload arc",
        "suggestions": ["Author opinion in local layer stack", "Move outside payload"]
    },
    "arc_type_local_over_specialize": {
        "detail": "Local arc (sublayer) is stronger than Specialize arc",
        "suggestions": ["Author opinion directly in local layer", "Specializes are weakest - avoid for opinions"]
    },
    "arc_type_local_over_relocate": {
        "detail": "Local arc (sublayer) is stronger than Relocate arc",
        "suggestions": ["Author opinion in local layer stack"]
    },
    
    # Inherit over weaker arcs
    "arc_type_inherit_over_variant": {
        "detail": "Inherit arc is stronger than Variant arc",
        "suggestions": ["Author opinion via Inherit instead of Variant", "Move to inherit class"]
    },
    "arc_type_inherit_over_reference": {
        "detail": "Inherit arc is stronger than Reference arc",
        "suggestions": ["Use Inherit for stronger composition", "Move opinion to inherited class"]
    },
    "arc_type_inherit_over_payload": {
        "detail": "Inherit arc is stronger than Payload arc",
        "suggestions": ["Author via Inherit arc", "Move outside payload"]
    },
    "arc_type_inherit_over_specialize": {
        "detail": "Inherit arc is stronger than Specialize arc",
        "suggestions": ["Use Inherit instead of Specialize for opinions"]
    },
    "arc_type_inherit_over_relocate": {
        "detail": "Inherit arc is stronger than Relocate arc",
        "suggestions": ["Author opinion via Inherit arc"]
    },
    
    # Variant over weaker arcs
    "arc_type_variant_over_reference": {
        "detail": "Variant arc is stronger than Reference arc",
        "suggestions": ["Author opinion in variant selection", "Move to variant layer"]
    },
    "arc_type_variant_over_payload": {
        "detail": "Variant arc is stronger than Payload arc",
        "suggestions": ["Author opinion in variant", "Move outside payload"]
    },
    "arc_type_variant_over_specialize": {
        "detail": "Variant arc is stronger than Specialize arc",
        "suggestions": ["Use Variant instead of Specialize"]
    },
    "arc_type_variant_over_relocate": {
        "detail": "Variant arc is stronger than Relocate arc",
        "suggestions": ["Author opinion in variant"]
    },
    
    # Relocate over weaker arcs (newer USD versions)
    "arc_type_relocate_over_reference": {
        "detail": "Relocate arc is stronger than Reference arc",
        "suggestions": ["Author opinion via Relocate"]
    },
    "arc_type_relocate_over_payload": {
        "detail": "Relocate arc is stronger than Payload arc",
        "suggestions": ["Author opinion via Relocate"]
    },
    "arc_type_relocate_over_specialize": {
        "detail": "Relocate arc is stronger than Specialize arc",
        "suggestions": ["Use Relocate instead of Specialize"]
    },
    
    # Reference over weaker arcs
    "arc_type_reference_over_payload": {
        "detail": "Reference arc is stronger than Payload arc",
        "suggestions": ["Author opinion in referenced layer", "Move from payload to reference"]
    },
    "arc_type_reference_over_specialize": {
        "detail": "Reference arc is stronger than Specialize arc",
        "suggestions": ["Use Reference instead of Specialize for opinions"]
    },
    
    # Payload over Specialize
    "arc_type_payload_over_specialize": {
        "detail": "Payload arc is stronger than Specialize arc",
        "suggestions": ["Use Payload instead of Specialize"]
    },
    
    # =========================================================================
    # SECONDARY ORDERING - same arc type, different resolution rules
    # =========================================================================
    
    "sublayer_order": {
        "detail": "Both opinions are in Local arc; blocker is higher in sublayer stack",
        "suggestions": [
            "Move your layer to a stronger position in sublayer stack",
            "Remove or modify the blocking opinion",
            "Reorder sublayers using subLayerPaths"
        ]
    },
    
    "direct_over_ancestral": {
        "detail": "Direct arc opinion beats ancestral arc opinion",
        "suggestions": [
            "Author opinion on direct arc at this prim",
            "Promote ancestral opinion to direct arc"
        ]
    },
    
    "listop_position": {
        "detail": "Earlier position in arc list wins (prepend vs append order)",
        "suggestions": [
            "Use prepend instead of append for arc composition",
            "Reorder arcs in composition list",
            "Author opinion in earlier arc"
        ]
    },
    
    # =========================================================================
    # LAYER STATE - environmental/loading issues
    # =========================================================================
    
    "layer_muted": {
        "detail": "User layer is muted; opinions ignored by stage",
        "suggestions": [
            "Unmute layer via stage.UnmuteLayer(layer_identifier)",
            "Check GetMutedLayers() for active mutes"
        ]
    },
    
    "payload_not_loaded": {
        "detail": "Prim's payload is not loaded; opinions inside are inaccessible",
        "suggestions": [
            "Load payload via stage.Load(prim_path)",
            "Set LoadAll policy when opening stage",
            "Check GetLoadRules() for loading configuration"
        ]
    },
    
    # =========================================================================
    # EXPLICIT BLOCKS
    # =========================================================================
    
    "attribute_blocked": {
        "detail": "Attribute has explicit value block (Sdf.ValueBlock)",
        "suggestions": [
            "Remove the blocking opinion from winning layer",
            "Override block with stronger arc type or sublayer",
            "Check for intentional attribute blocking"
        ]
    },
    
    "animation_blocked": {
        "detail": "Animation/timeSamples are blocked at this time",
        "suggestions": [
            "Remove animation block",
            "Use default value instead of timeSamples",
            "Check timeSample blocking at specific time codes"
        ]
    },
    
    # =========================================================================
    # EDGE CASES
    # =========================================================================
    
    "timesamples_over_default": {
        "detail": "TimeSamples in same spec override default value",
        "suggestions": [
            "Author timeSamples if you want time-varying values",
            "Clear timeSamples to use default value",
            "Check for unintended animation data"
        ]
    },
    
    "no_opinion_in_user_layer": {
        "detail": "Specified user layer has no opinion for this attribute",
        "suggestions": [
            "Author an opinion in your layer",
            "Verify correct layer identifier",
            "Check if layer is part of stage composition"
        ]
    },
    
    "user_opinion_is_winning": {
        "detail": "User's opinion is already the winning opinion",
        "suggestions": None
    },
}


def get_reason_detail(reason_code: str) -> str:
    """Get human-readable detail for a reason code."""
    return REASON_CODES.get(reason_code, {}).get("detail", "Unknown reason")


def get_suggestions(reason_code: str) -> list[str]:
    """Get actionable suggestions for a reason code."""
    suggestions = REASON_CODES.get(reason_code, {}).get("suggestions")
    if suggestions is None:
        return []
    if isinstance(suggestions, str):
        return [suggestions]
    return suggestions
