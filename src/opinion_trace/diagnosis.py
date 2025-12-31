"""
USD opinion diagnosis - pure analysis logic.

Receives extracted data and analyzes why user's opinion is blocked.
No USD API calls - enables testing with mock data.
"""

from dataclasses import dataclass

from .extraction import ExtractionResult, OpinionInfo
from .reason_codes import REASON_CODES, get_reason_detail, get_suggestions


@dataclass
class DiagnosisResult:
    """Result of diagnosing why a user's opinion is blocked."""
    user_layer_found: bool
    user_layer_index: int | None
    blocker_index: int | None
    blocker_layer: str | None
    reason: str                     # reason code
    reason_detail: str
    suggestions: list[str]


def diagnose(extraction: ExtractionResult, user_layer: str) -> DiagnosisResult | None:
    """
    Analyze why user's opinion is blocked.
    Receives pure data, no USD API calls.
    
    Args:
        extraction: Extracted opinion data from USD
        user_layer: User's layer identifier or basename to diagnose
        
    Returns:
        DiagnosisResult explaining why user's opinion is blocked, or None if extraction failed
    """
    if extraction.error:
        return None
    
    # 1. Find user opinion
    user_opinion = find_user_opinion(extraction.opinions, user_layer)
    if not user_opinion:
        return DiagnosisResult(
            user_layer_found=False,
            user_layer_index=None,
            blocker_index=None,
            blocker_layer=None,
            reason="no_opinion_in_user_layer",
            reason_detail=get_reason_detail("no_opinion_in_user_layer"),
            suggestions=get_suggestions("no_opinion_in_user_layer"),
        )
    
    # 2. User is winner?
    if user_opinion.index == 0:
        return DiagnosisResult(
            user_layer_found=True,
            user_layer_index=0,
            blocker_index=None,
            blocker_layer=None,
            reason="user_opinion_is_winning",
            reason_detail=get_reason_detail("user_opinion_is_winning"),
            suggestions=get_suggestions("user_opinion_is_winning"),
        )
    
    winner = extraction.opinions[0]
    
    # 3. Run checks in order
    reason = run_checks(extraction, winner, user_opinion)
    
    return DiagnosisResult(
        user_layer_found=True,
        user_layer_index=user_opinion.index,
        blocker_index=0,
        blocker_layer=winner.layer_name,
        reason=reason,
        reason_detail=get_reason_detail(reason),
        suggestions=get_suggestions(reason),
    )


def find_user_opinion(opinions: list[OpinionInfo], user_layer: str) -> OpinionInfo | None:
    """
    Find opinion matching user's layer (by identifier or basename).
    
    Args:
        opinions: List of all opinions from extraction
        user_layer: User's layer identifier or basename
        
    Returns:
        Matching OpinionInfo or None if not found
    """
    for op in opinions:
        if user_layer in (op.layer_identifier, op.layer_name):
            return op
    return None


def run_checks(
    extraction: ExtractionResult, 
    winner: OpinionInfo, 
    user: OpinionInfo
) -> str:
    """
    Waterfall of checks. Returns first matching reason code.
    
    Checks are ordered by priority:
    1. Layer state (muted, unloaded)
    2. Explicit blocks
    3. Arc type comparison
    4. Secondary ordering (same arc type)
    
    Args:
        extraction: Full extraction result
        winner: Winning opinion (index 0)
        user: User's opinion
        
    Returns:
        Reason code string
    """
    # 1. Layer state checks
    reason = _check_layer_muted(extraction, user)
    if reason:
        return reason
    
    reason = _check_payload_loaded(extraction)
    if reason:
        return reason
    
    # 2. Explicit block checks
    reason = _check_explicit_block(winner)
    if reason:
        return reason
    
    # 3. Arc type comparison
    reason = _check_arc_types(winner, user)
    if reason:
        return reason
    
    # 4. Same arc type - secondary ordering
    return _check_secondary_ordering(winner, user)


def _check_layer_muted(extraction: ExtractionResult, user: OpinionInfo) -> str | None:
    """
    Check if user's layer is muted.
    
    Args:
        extraction: Full extraction result
        user: User's opinion
        
    Returns:
        "layer_muted" if muted, None otherwise
    """
    if extraction.layer_muting.get(user.layer_identifier, False):
        return "layer_muted"
    return None


def _check_payload_loaded(extraction: ExtractionResult) -> str | None:
    """
    Check if prim's payload is loaded.
    
    Args:
        extraction: Full extraction result
        
    Returns:
        "payload_not_loaded" if not loaded, None otherwise
    """
    if not extraction.prim_is_loaded:
        return "payload_not_loaded"
    return None


def _check_explicit_block(winner: OpinionInfo) -> str | None:
    """
    Check if winner has explicit block.
    
    Args:
        winner: Winning opinion
        
    Returns:
        "attribute_blocked" if blocked, None otherwise
    """
    if winner.is_blocked:
        return "attribute_blocked"
    return None


def _check_arc_types(winner: OpinionInfo, user: OpinionInfo) -> str | None:
    """
    Check if different arc types explain the blocking.
    
    Uses LIVRPS hierarchy: Local > Inherit > Variant > Relocate > Reference > Payload > Specialize
    
    Args:
        winner: Winning opinion
        user: User's opinion
        
    Returns:
        Reason code like "arc_type_local_over_reference" if different arc types, None if same
    """
    if winner.arc_type != user.arc_type:
        # Generate reason code: arc_type_{winner}_over_{user}
        reason = f"arc_type_{winner.arc_type.lower()}_over_{user.arc_type.lower()}"
        
        # Validate it exists in REASON_CODES
        if reason in REASON_CODES:
            return reason
        
        # Fallback - We know this is about different arc types, but reason code not defined
        return "listop_position"
    
    return None


def _check_secondary_ordering(winner: OpinionInfo, user: OpinionInfo) -> str:
    """
    Check secondary ordering rules when arc types match.
    
    Rules in order:
    1. Sublayer order (both Local)
    2. Direct vs ancestral
    3. List operation position (prepend vs append)
    
    Args:
        winner: Winning opinion
        user: User's opinion
        
    Returns:
        Reason code for secondary ordering
    """
    # Both local - sublayer ordering
    if winner.arc_type == "Local":
        return "sublayer_order"
    
    # Direct beats ancestral
    if winner.is_direct and not user.is_direct:
        return "direct_over_ancestral"
    
    # Default: list operation position
    return "listop_position"
