"""
CLI interface for USD opinion trace tool.

Provides argparse-based command-line interface with JSON output.
Orchestrates extraction and diagnosis phases.
"""

import argparse
import json
import sys

from .extraction import extract_opinions
from .diagnosis import diagnose


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Diagnose why a USD opinion is blocked in composition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full diagnosis
  %(prog)s shot.usd /World/Chair xformOp:translate lighting.usd
  
  # Stack only (no diagnosis)
  %(prog)s shot.usd /World/Chair xformOp:translate --stack-only
        """
    )
    
    parser.add_argument('stage', help='Path to USD stage')
    parser.add_argument('prim_path', help='Prim path (e.g., /World/Chair)')
    parser.add_argument('attribute', help='Attribute name (e.g., xformOp:translate)')
    parser.add_argument('layer', help='User layer to diagnose (identifier or basename)')
    parser.add_argument('--time', type=float, default=None, 
                       help='Time code for time-sampled data (default: Default time)')
    parser.add_argument('--stack-only', action='store_true', 
                       help='Output opinion stack without diagnosis')
    
    args = parser.parse_args()
    
    # Phase 1: Extract (always)
    extraction = extract_opinions(args.stage, args.prim_path, args.attribute, args.time)
    
    if extraction.error:
        output_error(extraction.error)
        return 1
    
    # Phase 2: Diagnose (unless --stack-only)
    diagnosis_result = None
    if not args.stack_only:
        diagnosis_result = diagnose(extraction, args.layer)
    
    # Phase 3: Output
    result = build_output(extraction, diagnosis_result, args.layer)
    print(json.dumps(result, indent=2, default=str))
    
    return 0


def build_output(extraction, diagnosis, user_layer: str | None) -> dict:
    """
    Combine extraction + diagnosis into final output dict.
    
    Args:
        extraction: ExtractionResult from extraction phase
        diagnosis: DiagnosisResult from diagnosis phase (or None if --stack-only)
        user_layer: User's layer identifier/basename (or None if --stack-only)
        
    Returns:
        Dictionary ready for JSON serialization
    """
    return {
        "query": {
            "stage": extraction.stage_path,
            "prim_path": extraction.prim_path,
            "attribute": extraction.attr_name,
            "user_layer": user_layer,
            "time": extraction.time_code,
        },
        "resolved_value": extraction.resolved_value,
        "resolved_value_type": extraction.resolved_value_type,
        "opinions": [
            {
                "index": o.index,
                "layer": o.layer_name,
                "layer_identifier": o.layer_identifier,
                "arc_type": o.arc_type,
                "value": o.value,
                "has_timesamples": o.has_timesamples,
                "is_blocked": o.is_blocked,
                "status": "winning" if o.index == 0 else "blocked",
                "is_user_layer": user_layer and user_layer in (o.layer_identifier, o.layer_name),
                "is_direct": o.is_direct,
            }
            for o in extraction.opinions
        ],
        "diagnosis": diagnosis.__dict__ if diagnosis else None,
        "error": extraction.error,
    }


def output_error(error: dict):
    """
    Output error information.
    
    Args:
        error: Error dict with 'code' and 'message' keys
    """
    print(json.dumps({"error": error}, indent=2))


if __name__ == '__main__':
    sys.exit(main())
