"""
Reason codes for USD opinion composition diagnosis.

Each code maps to a detailed explanation and actionable suggestions.
Organized by category: arc types, secondary ordering, layer states, blocks, edge cases.

Structure for GUI display:
- arc_descriptions: Short "X is for Y" explanations (display together)
- scenarios: "If you want..." conditional guidance (display as options)
"""

REASON_CODES = {
    # =========================================================================
    # ARC TYPE COMPARISONS - LIVRPS hierarchy
    # =========================================================================
    
    # Local over everything
    "arc_type_local_over_inherit": {
        "arc_descriptions": {
            "local": "change just this one tree's color to red (instance-specific edits)",
            "inherit": "make all pine trees in the forest darker (mass-editing a category)"
        },
        "scenarios": [
            {
                "condition": "this specific instance to be different from the class",
                "action": "keep the Local edit - this is working as intended"
            },
            {
                "condition": "all instances including this one to follow the class rules",
                "action": "remove the Local edit and let the Inherit control it"
            },
            {
                "condition": "to make changes to all objects of this type",
                "action": "edit the Inherit class itself instead of making Local overrides on each instance"
            }
        ]
    },
    
    "arc_type_local_over_variant": {
        "arc_descriptions": {
            "local": "force this asset to always use the red material (fixed instance settings)",
            "variant": "let users switch between red/blue/green materials (switchable options)"
        },
        "scenarios": [
            {
                "condition": "this instance locked to a specific look regardless of variant selection",
                "action": "keep the Local edit - it will always override the variant"
            },
            {
                "condition": "the variant switching to work on this instance",
                "action": "remove the Local edit and let the Variant control the property"
            },
            {
                "condition": "to change what a variant option looks like for all instances",
                "action": "edit within the Variant definition itself rather than overriding locally"
            }
        ]
    },
    
    "arc_type_local_over_reference": {
        "arc_descriptions": {
            "local": "adjust this imported chair to be 10% bigger in my scene (scene-specific tweaks)",
            "reference": "bring in the chair_model.usd asset (importing external content)"
        },
        "scenarios": [
            {
                "condition": "scene-specific adjustments to this Referenced asset",
                "action": "keep the Local edit - this is the correct workflow"
            },
            {
                "condition": "the change to affect the asset everywhere it's used",
                "action": "edit the source Referenced file instead of overriding locally"
            },
            {
                "condition": "the Referenced asset to work exactly as authored",
                "action": "remove the Local override and use the asset as-is"
            }
        ]
    },
    
    "arc_type_local_over_payload": {
        "arc_descriptions": {
            "local": "make this heavy building visible/invisible in my scene (scene-level control)",
            "payload": "load this 50GB city block only when needed (deferred loading of heavy content)"
        },
        "scenarios": [
            {
                "condition": "to override properties of this heavy asset in your scene",
                "action": "keep the Local edit - Payloads are meant to be overridden locally"
            },
            {
                "condition": "the Payload to load with its original settings",
                "action": "remove the Local edit and let the Payload define the defaults"
            },
            {
                "condition": "better performance by not loading heavy data",
                "action": "unload the Payload rather than trying to override it locally"
            }
        ]
    },
    
    "arc_type_local_over_specialize": {
        "arc_descriptions": {
            "local": "this specific material should be glossy=0.8 (explicit values)",
            "specialize": "if nothing else is set, use glossy=0.5 as the default (fallback values)"
        },
        "scenarios": [
            {
                "condition": "an explicit value on this instance",
                "action": "keep the Local edit - Specializes are designed to be overridden"
            },
            {
                "condition": "to use the fallback default value",
                "action": "remove the Local edit and let the Specialize provide it"
            },
            {
                "condition": "to change the default for all objects that use it",
                "action": "edit the Specialize source instead of overriding each instance locally"
            }
        ]
    },
    
    "arc_type_local_over_relocate": {
        "arc_descriptions": {
            "local": "direct edits in your current layer (strongest opinions)",
            "relocate": "move/redirect prim paths during composition"
        },
        "scenarios": [
            {
                "condition": "to override the relocated prim's properties",
                "action": "keep the Local edit - it will override the Relocate"
            },
            {
                "condition": "the Relocate to work as intended",
                "action": "remove conflicting Local edits"
            }
        ]
    },
    
    # Inherit over weaker arcs
    "arc_type_inherit_over_variant": {
        "arc_descriptions": {
            "inherit": "make all cars in the scene have chrome wheels (mass-edit across types)",
            "variant": "this car can switch between sport/luxury/economy versions (switchable configurations)"
        },
        "scenarios": [
            {
                "condition": "to enforce a property across all instances regardless of variant choice",
                "action": "keep the Inherit - it's overriding variants intentionally"
            },
            {
                "condition": "variants to control the look independently per instance",
                "action": "remove the Inherit or restructure so Inherit and Variants affect different properties"
            },
            {
                "condition": "each variant to have different inherited behavior",
                "action": "create separate Inherit classes for each variant rather than one Inherit overriding all variants"
            }
        ]
    },
    
    "arc_type_inherit_over_reference": {
        "arc_descriptions": {
            "inherit": "make all pine trees in the forest 10% darker (mass-editing a category of objects)",
            "reference": "bring the hero_pine_tree.usd asset into this scene (importing specific assets)"
        },
        "scenarios": [
            {
                "condition": "to use this specific Referenced asset with its own unique properties",
                "action": "remove the Inherit or move your Reference to a different part of the hierarchy where the Inherit doesn't apply"
            },
            {
                "condition": "all objects of this type to follow the same class rules consistently",
                "action": "keep the Inherit and remove the Reference - the Inherit is doing its job by enforcing consistency"
            },
            {
                "condition": "to combine both (use the class template but add specific details from a Reference)",
                "action": "restructure your setup: put the Reference under a child prim, or make sure the Inherit and Reference affect different properties, or use Variants within the inherited class instead"
            },
            {
                "condition": "to make just this one instance different from the class",
                "action": "remove the Inherit from this instance and add a Local override instead - the Reference can then work as intended"
            }
        ]
    },
    
    "arc_type_inherit_over_payload": {
        "arc_descriptions": {
            "inherit": "all buildings should have this lighting rig (mass-applying properties to categories)",
            "payload": "load this detailed building model only when working on it (deferred loading)"
        },
        "scenarios": [
            {
                "condition": "to apply consistent properties to all Payload instances without loading them",
                "action": "keep the Inherit - this is a powerful optimization pattern"
            },
            {
                "condition": "the Payload's authored data to control the instance",
                "action": "remove the Inherit or make it affect different properties"
            },
            {
                "condition": "to mass-edit Payload instances while keeping them unloaded",
                "action": "use Inherits on the Payload wrapper prims - this lets you control visibility, transforms, etc. without loading heavy geometry"
            }
        ]
    },
    
    "arc_type_inherit_over_specialize": {
        "arc_descriptions": {
            "inherit": "all metal materials get roughness=0.2 (active mass-edits)",
            "specialize": "if no one sets roughness, default to 0.5 (passive fallbacks)"
        },
        "scenarios": [
            {
                "condition": "to actively enforce a value across all instances",
                "action": "keep the Inherit - it's designed to override Specializes"
            },
            {
                "condition": "Specializes to provide the default",
                "action": "remove the Inherit - but note that Specializes are meant to be overridden by stronger arcs"
            },
            {
                "condition": "different defaults for different categories",
                "action": "use Inherits to define category-specific rules rather than relying on Specializes alone"
            }
        ]
    },
    
    "arc_type_inherit_over_relocate": {
        "arc_descriptions": {
            "inherit": "mass-edit all objects of a type (class-based changes)",
            "relocate": "move/redirect prim paths during composition"
        },
        "scenarios": [
            {
                "condition": "class-based edits to apply to relocated prims",
                "action": "keep the Inherit - it will apply after relocation"
            },
            {
                "condition": "the Relocate to work without inherited overrides",
                "action": "remove the Inherit or ensure it targets different properties"
            }
        ]
    },
    
    # Variant over weaker arcs
    "arc_type_variant_over_reference": {
        "arc_descriptions": {
            "variant": "switch this prop between damaged/pristine versions (selectable options within an asset)",
            "reference": "bring in the prop_base.usd asset (importing the asset foundation)"
        },
        "scenarios": [
            {
                "condition": "the variant selection to control what's visible",
                "action": "keep the Variant - variants often contain References inside them"
            },
            {
                "condition": "the Reference to always contribute regardless of variant",
                "action": "move the Reference outside/above the Variant in the hierarchy"
            },
            {
                "condition": "different References for each variant option",
                "action": "put References inside each variant definition - this is a common pattern for LOD switching"
            }
        ]
    },
    
    "arc_type_variant_over_payload": {
        "arc_descriptions": {
            "variant": "switch between summer/winter/fall versions of this landscape (seasonal variants)",
            "payload": "defer loading the heavy landscape geometry (performance management)"
        },
        "scenarios": [
            {
                "condition": "to switch between different heavy assets efficiently",
                "action": "put Payloads inside each Variant option - users can switch variants without loading all options"
            },
            {
                "condition": "the Payload to always load regardless of variant",
                "action": "place the Payload outside the Variant in the hierarchy"
            },
            {
                "condition": "variant switching without loading heavy data",
                "action": "use Variants that contain different Payload references - this is the recommended pattern for LOD variants"
            }
        ]
    },
    
    "arc_type_variant_over_specialize": {
        "arc_descriptions": {
            "variant": "switch this character between child/teen/adult body types (distinct options)",
            "specialize": "if no body type is chosen, default to adult (fallback)"
        },
        "scenarios": [
            {
                "condition": "explicit variant control",
                "action": "keep the Variant - it's designed to override Specializes"
            },
            {
                "condition": "the Specialize fallback to work",
                "action": "remove the Variant or ensure variants don't define the same properties"
            },
            {
                "condition": "variants with smart defaults",
                "action": "use Specializes to set base values, then Variants to offer explicit choices - they work well together"
            }
        ]
    },
    
    "arc_type_variant_over_relocate": {
        "arc_descriptions": {
            "variant": "switch between different options (selectable configurations)",
            "relocate": "move/redirect prim paths during composition"
        },
        "scenarios": [
            {
                "condition": "variant selection to control relocated paths",
                "action": "keep the Variant - it can control what gets relocated"
            },
            {
                "condition": "the Relocate to work independently of variants",
                "action": "move the Relocate outside the Variant scope"
            }
        ]
    },
    
    # Relocate over weaker arcs (newer USD versions)
    "arc_type_relocate_over_reference": {
        "arc_descriptions": {
            "relocate": "move/redirect prim paths during composition",
            "reference": "bring in external assets"
        },
        "scenarios": [
            {
                "condition": "to redirect where Referenced content appears",
                "action": "keep the Relocate - it will move the Reference target"
            },
            {
                "condition": "the Reference to appear at its original location",
                "action": "remove the Relocate"
            }
        ]
    },
    
    "arc_type_relocate_over_payload": {
        "arc_descriptions": {
            "relocate": "move/redirect prim paths during composition",
            "payload": "defer loading of heavy content"
        },
        "scenarios": [
            {
                "condition": "to redirect where Payload content loads",
                "action": "keep the Relocate - it will move the Payload target"
            },
            {
                "condition": "the Payload to load at its original location",
                "action": "remove the Relocate"
            }
        ]
    },
    
    "arc_type_relocate_over_specialize": {
        "arc_descriptions": {
            "relocate": "move/redirect prim paths during composition",
            "specialize": "provide fallback default values"
        },
        "scenarios": [
            {
                "condition": "to redirect specialized content",
                "action": "keep the Relocate"
            },
            {
                "condition": "Specializes to work at original paths",
                "action": "remove the Relocate or adjust the path mapping"
            }
        ]
    },
    
    # Reference over weaker arcs
    "arc_type_reference_over_payload": {
        "arc_descriptions": {
            "reference": "bring in the building_exterior.usd (always-loaded modular content)",
            "payload": "defer loading building_interior.usd until needed (optional heavy content)"
        },
        "scenarios": [
            {
                "condition": "the lightweight exterior always loaded and interior optionally loaded",
                "action": "use Reference for exterior, Payload for interior - this is the standard pattern"
            },
            {
                "condition": "both to be deferrable",
                "action": "convert the Reference to a Payload so users can choose what to load"
            },
            {
                "condition": "the Payload's data to be accessible",
                "action": "remove the blocking Reference or ensure they target different parts of the namespace"
            },
            {
                "condition": "to see what's preventing your Payload from working",
                "action": "check if a Reference is already bringing in similar data and causing a conflict"
            }
        ]
    },
    
    "arc_type_reference_over_specialize": {
        "arc_descriptions": {
            "reference": "bring in the metal_shader.usd asset (explicit asset inclusion)",
            "specialize": "if no shader is assigned, use default_gray.usd (fallback)"
        },
        "scenarios": [
            {
                "condition": "a specific shader assigned",
                "action": "keep the Reference - it's designed to override Specializes"
            },
            {
                "condition": "to rely on the fallback",
                "action": "remove the Reference and let Specializes provide the default"
            },
            {
                "condition": "References with smart fallbacks",
                "action": "use Specializes for defaults and References for explicit assignments - this is a good pattern for optional overrides"
            }
        ]
    },
    
    # Payload over Specialize
    "arc_type_payload_over_specialize": {
        "arc_descriptions": {
            "payload": "load this heavy asset when needed (deferred loading of substantial content)",
            "specialize": "use these fallback values if nothing else is set (defaults)"
        },
        "scenarios": [
            {
                "condition": "the Payload's data to define the asset",
                "action": "keep the Payload - it should override Specializes"
            },
            {
                "condition": "defaults before the Payload loads",
                "action": "use Specializes to set preview/proxy values that show until the full Payload is loaded"
            },
            {
                "condition": "smart loading",
                "action": "Specializes can provide lightweight placeholders while Payloads bring in full detail - this is useful for progressive loading"
            }
        ]
    },
    
    # =========================================================================
    # SECONDARY ORDERING - same arc type, different resolution rules
    # =========================================================================
    
    "sublayer_order": {
        "detail": "Both opinions are in Local arc; blocker is higher in sublayer stack",
        "scenarios": [
            {
                "condition": "your edit to win",
                "action": "move your layer to a stronger position in sublayer stack"
            },
            {
                "condition": "the current opinion to remain",
                "action": "keep the sublayer order as-is"
            },
            {
                "condition": "to reorganize layers",
                "action": "reorder sublayers using subLayerPaths"
            }
        ]
    },
    
    "direct_over_ancestral": {
        "detail": "Direct arc opinion beats ancestral arc opinion",
        "scenarios": [
            {
                "condition": "your edit to take priority",
                "action": "author opinion on direct arc at this prim"
            },
            {
                "condition": "the ancestral opinion to apply",
                "action": "remove the direct arc opinion"
            },
            {
                "condition": "to make the ancestral opinion direct",
                "action": "promote ancestral opinion to direct arc on this prim"
            }
        ]
    },
    
    "listop_position": {
        "detail": "Earlier position in arc list wins (prepend vs append order)",
        "scenarios": [
            {
                "condition": "your arc to take priority",
                "action": "use prepend instead of append for arc composition"
            },
            {
                "condition": "different arc ordering",
                "action": "reorder arcs in composition list"
            },
            {
                "condition": "your opinion to win",
                "action": "author opinion in earlier arc"
            }
        ]
    },
    
    # =========================================================================
    # LAYER STATE - environmental/loading issues
    # =========================================================================
    
    "layer_muted": {
        "detail": "User layer is muted; opinions ignored by stage",
        "scenarios": [
            {
                "condition": "this layer's opinions to be active",
                "action": "unmute layer via stage.UnmuteLayer(layer_identifier)"
            },
            {
                "condition": "to see which layers are muted",
                "action": "check GetMutedLayers() for active mutes"
            },
            {
                "condition": "to keep the layer muted",
                "action": "no action needed - layer will remain muted"
            }
        ]
    },
    
    "payload_not_loaded": {
        "detail": "Prim's payload is not loaded; opinions inside are inaccessible",
        "scenarios": [
            {
                "condition": "to access the Payload's opinions",
                "action": "load payload via stage.Load(prim_path)"
            },
            {
                "condition": "all payloads loaded by default",
                "action": "set LoadAll policy when opening stage"
            },
            {
                "condition": "to check loading configuration",
                "action": "check GetLoadRules() for current loading rules"
            },
            {
                "condition": "to keep the Payload unloaded for performance",
                "action": "no action needed - this is working as intended"
            }
        ]
    },
    
    # =========================================================================
    # EXPLICIT BLOCKS
    # =========================================================================
    
    "attribute_blocked": {
        "detail": "Attribute has explicit value block (Sdf.ValueBlock)",
        "scenarios": [
            {
                "condition": "this attribute to have a value",
                "action": "remove the blocking opinion from winning layer"
            },
            {
                "condition": "to override the block",
                "action": "author opinion with stronger arc type or in stronger sublayer"
            },
            {
                "condition": "to verify the block is intentional",
                "action": "check if attribute blocking is intentional for this workflow"
            }
        ]
    },
    
    "animation_blocked": {
        "detail": "Animation/timeSamples are blocked at this time",
        "scenarios": [
            {
                "condition": "animation to work",
                "action": "remove animation block from stronger layer"
            },
            {
                "condition": "to use static values",
                "action": "use default value instead of timeSamples"
            },
            {
                "condition": "to investigate the block",
                "action": "check timeSample blocking at specific time codes"
            }
        ]
    },
    
    # =========================================================================
    # EDGE CASES
    # =========================================================================
    
    "timesamples_over_default": {
        "detail": "TimeSamples in same spec override default value",
        "scenarios": [
            {
                "condition": "time-varying animation",
                "action": "keep timeSamples - this is working as intended"
            },
            {
                "condition": "static values",
                "action": "clear timeSamples to use default value"
            },
            {
                "condition": "to verify animation data",
                "action": "check for unintended animation data that might be overriding defaults"
            }
        ]
    },
    
    "no_opinion_in_user_layer": {
        "detail": "Specified user layer has no opinion for this attribute",
        "scenarios": [
            {
                "condition": "to add an opinion in this layer",
                "action": "author an opinion in your layer"
            },
            {
                "condition": "to verify layer setup",
                "action": "verify correct layer identifier and check if layer is part of stage composition"
            }
        ]
    },
    
    "user_opinion_is_winning": {
        "detail": "User's opinion is already the winning opinion",
        "scenarios": []
    },
}


def get_arc_descriptions(reason_code: str) -> dict:
    """Get arc descriptions for display."""
    return REASON_CODES.get(reason_code, {}).get("arc_descriptions", {})


def get_detail(reason_code: str) -> str:
    """Get human-readable detail for a reason code."""
    return REASON_CODES.get(reason_code, {}).get("detail", "")


def get_scenarios(reason_code: str) -> list:
    """Get scenario-based suggestions."""
    return REASON_CODES.get(reason_code, {}).get("scenarios", [])


def get_reason_detail(reason_code: str) -> str:
    """Get human-readable detail for a reason code.
    
    Handles both old format (detail string) and new format (arc_descriptions).
    """
    code_data = REASON_CODES.get(reason_code, {})
    
    # Try old format first
    if "detail" in code_data:
        return code_data["detail"]
    
    # Build detail from arc_descriptions if available
    arc_descs = code_data.get("arc_descriptions", {})
    if arc_descs:
        parts = [f"{arc.title()} is for: {desc}" for arc, desc in arc_descs.items()]
        return " | ".join(parts)
    
    return ""


def get_suggestions(reason_code: str) -> list[str]:
    """Get actionable suggestions for a reason code.
    
    Handles both old format (suggestions list) and new format (scenarios).
    """
    code_data = REASON_CODES.get(reason_code, {})
    
    # Try old format first
    if "suggestions" in code_data:
        return code_data["suggestions"]
    
    # Convert scenarios to suggestion strings
    scenarios = code_data.get("scenarios", [])
    suggestions = []
    for scenario in scenarios:
        condition = scenario.get("condition", "")
        action = scenario.get("action", "")
        if condition and action:
            suggestions.append(f"If you want {condition}: {action}")
    
    return suggestions