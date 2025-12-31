"""CLI tests for USD Opinion Trace tool.

Tests each reason code by invoking the CLI as a subprocess and validating JSON output.
"""

import json
import os
import subprocess
import sys
from pxr import Usd, Pcp


def run_cli(*args):
    """
    Run the CLI script with given arguments.
    
    Returns:
        subprocess.CompletedProcess
    """
    # Use the same Python interpreter running the tests
    python_exe = sys.executable
    
    # Get script path from conftest fixture pattern
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cli_script = os.path.join(repo_root, "usd_opinion_trace.py")
    
    result = subprocess.run(
        [python_exe, cli_script] + list(args),
        capture_output=True,
        text=True,
    )
    return result


def get_diagnosis(*args):
    """
    Run CLI and return parsed diagnosis dict.
    
    Returns:
        dict: Parsed JSON output
    """
    result = run_cli(*args)
    if result.returncode != 0:
        raise RuntimeError(f"CLI failed: {result.stderr}")
    
    output = json.loads(result.stdout)
    return output

def assert_matches_flattened(output, stage_path: str, prim_path: str, attr_name: str):
    """
    Assert that CLI output matches USD's composed result (ground truth).
    Compares resolved value and winning arc type.
    """
    stage = Usd.Stage.Open(stage_path)
    prim = stage.GetPrimAtPath(prim_path)
    attr = prim.GetAttribute(attr_name)
    
    expected_value = attr.Get()
    
    resolve_info = attr.GetResolveInfo()
    node = resolve_info.GetNode()
    arc_type = node.arcType
    
    # Map PcpArcType to string matching reason codes
    arc_type_map = {
        Pcp.ArcTypeRoot: "Local",
        Pcp.ArcTypeInherit: "Inherit",
        Pcp.ArcTypeVariant: "Variant",
        Pcp.ArcTypeReference: "Reference",
        Pcp.ArcTypePayload: "Payload",
        Pcp.ArcTypeSpecialize: "Specialize",
    }
    expected_arc = arc_type_map.get(arc_type, str(arc_type))
    
    assert output["resolved_value"] == expected_value, \
        f"Value mismatch: got {output['resolved_value']}, expected {expected_value}"
    assert output["opinions"][0]["arc_type"] == expected_arc, \
        f"Arc type mismatch: got {output['opinions'][0]['arc_type']}, expected {expected_arc}"

class TestLIVRPSConflicts:
    """Test LIVRPS arc type hierarchy conflicts."""
    
    def test_local_over_reference(self, stages_dir):
        """Test local opinion blocking reference opinion."""
        stage = os.path.join(stages_dir, "stage_local_over_reference.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "ref_target.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "arc_type_local_over_reference"
        assert output["diagnosis"]["user_layer_found"] is True
        assert output["diagnosis"]["blocker_layer"] == "stage_local_over_reference.usda"
    
    def test_local_over_payload(self, stages_dir):
        """Test local opinion blocking payload opinion."""
        stage = os.path.join(stages_dir, "stage_local_over_payload.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "ref_target.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "arc_type_local_over_payload"
        assert output["diagnosis"]["user_layer_found"] is True
    
    def test_local_over_inherit(self, stages_dir):
        """Test local opinion blocking inherit opinion."""
        stage = os.path.join(stages_dir, "stage_local_over_inherit.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "stage_local_over_inherit.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        # Note: Both opinions are in same layer, so we expect the local arc to win
        assert output["diagnosis"]["reason"] in ["arc_type_local_over_inherit", "user_opinion_is_winning"]
    
    def test_local_over_variant(self, stages_dir):
        """Test local opinion blocking variant opinion."""
        stage = os.path.join(stages_dir, "stage_local_over_variant.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "stage_local_over_variant.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] in ["arc_type_local_over_variant", "user_opinion_is_winning"]
    
    def test_local_over_specialize(self, stages_dir):
        """Test local opinion blocking specialize opinion."""
        stage = os.path.join(stages_dir, "stage_local_over_specialize.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "stage_local_over_specialize.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] in ["arc_type_local_over_specialize", "user_opinion_is_winning"]
    
    def test_inherit_over_variant(self, stages_dir):
        """Test inherit opinion blocking variant opinion."""
        stage = os.path.join(stages_dir, "stage_inherit_over_variant.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "stage_inherit_over_variant.usda")
        #print(output)  # TODO: temporary, remove later
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] in ["arc_type_inherit_over_variant", "user_opinion_is_winning"]
    
    def test_inherit_over_reference(self, stages_dir):
        """Test inherit opinion blocking reference opinion."""
        stage = os.path.join(stages_dir, "stage_inherit_over_reference.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "ref_target.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "arc_type_inherit_over_reference"
        assert output["diagnosis"]["user_layer_found"] is True
    
    def test_variant_over_reference(self, stages_dir):
        """Test variant opinion blocking reference opinion."""
        stage = os.path.join(stages_dir, "stage_variant_over_reference.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "ref_target.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "arc_type_variant_over_reference"
        assert output["diagnosis"]["user_layer_found"] is True
    
    def test_variant_over_payload(self, stages_dir):
        """Test variant opinion blocking payload opinion."""
        stage = os.path.join(stages_dir, "stage_variant_over_payload.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "ref_target.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "arc_type_variant_over_payload"
        assert output["diagnosis"]["user_layer_found"] is True
    
    def test_reference_over_payload(self, stages_dir):
        """Test reference opinion blocking payload opinion."""
        stage = os.path.join(stages_dir, "stage_reference_over_payload.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "ref_target.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "arc_type_reference_over_payload"
        assert output["diagnosis"]["user_layer_found"] is True


class TestSameArcOrdering:
    """Test ordering within same arc type."""
    
    def test_sublayer_order(self, stages_dir):
        """Test sublayer ordering - stronger sublayer wins."""
        stage = os.path.join(stages_dir, "stage_sublayer_order.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "sublayer_weak.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "sublayer_order"
        assert output["diagnosis"]["user_layer_found"] is True
        assert output["diagnosis"]["blocker_layer"] == "sublayer_strong.usda"
    
    def test_reference_order(self, stages_dir):
        """Test reference list ordering - first reference wins."""
        stage = os.path.join(stages_dir, "stage_reference_order.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "stage_reference_order.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        # Note: This tests listop_position since both refs are in same file
        assert output["diagnosis"]["reason"] in ["listop_position", "user_opinion_is_winning"]


class TestUserLayerIssues:
    """Test user layer identification and status."""
    
    def test_user_layer_not_in_stack(self, stages_dir):
        """Test error when user layer is not in composition."""
        stage = os.path.join(stages_dir, "stage_simple.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "nonexistent.usda")
        
        assert output["diagnosis"]["reason"] == "no_opinion_in_user_layer"
        assert output["diagnosis"]["user_layer_found"] is False
    
    def test_user_layer_is_winning(self, stages_dir):
        """Test when user's opinion is already winning."""
        stage = os.path.join(stages_dir, "stage_sublayer_order.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "sublayer_strong.usda")
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "user_opinion_is_winning"
        assert output["diagnosis"]["user_layer_found"] is True


class TestAttributePrimIssues:
    """Test error cases for prims and attributes."""
    
    def test_prim_not_found(self, stages_dir):
        """Test error when prim doesn't exist."""
        stage = os.path.join(stages_dir, "stage_simple.usda")
        result = run_cli(stage, "/WrongPrim", "size", "dummy.usda", "--stack-only")
        
        assert result.returncode != 0
        output_str = result.stdout or result.stderr
        output = json.loads(output_str)
        assert output["error"]["code"] == "PRIM_NOT_FOUND"
    
    def test_attr_not_found(self, stages_dir):
        """Test error when attribute doesn't exist."""
        stage = os.path.join(stages_dir, "stage_simple.usda")
        result = run_cli(stage, "/ExampleAsset", "wrongAttr", "dummy.usda")
        
        assert result.returncode != 0
        output = json.loads(result.stdout)
        assert output["error"]["code"] == "ATTR_NOT_FOUND"
    
    def test_attr_no_opinions(self, stages_dir):
        """Test attribute with no authored opinions."""
        stage = os.path.join(stages_dir, "stage_fallback_only.usda")
        result = run_cli(stage, "/ExampleAsset", "size", "dummy.usda", "--stack-only")
        
        # Should fail with NO_VALID_OPINIONS error
        assert result.returncode != 0
        output = json.loads(result.stdout)
        assert output["error"]["code"] == "NO_VALID_OPINIONS"
    
    def test_value_blocked(self, stages_dir):
        """Test explicit value block."""
        stage = os.path.join(stages_dir, "stage_value_blocked.usda")
        output = get_diagnosis(stage, "/ExampleAsset", "size", "sublayer_weak.usda")
        
        assert output["resolved_value"] is None
        assert output["diagnosis"]["reason"] == "attribute_blocked"
        assert output["diagnosis"]["user_layer_found"] is True


class TestTimeRelated:
    """Test time-sampled attribute handling."""
    
    def test_default_blocks_timesamples(self, stages_dir):
        """Test default value in stronger layer blocking timeSamples."""
        stage = os.path.join(stages_dir, "stage_default_vs_timesamples.usda")
        output = get_diagnosis(
            stage, "/ExampleAsset", "size", 
            "sublayer_with_timesamples.usda",
            "--time", "1"
        )
        
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"]["reason"] == "sublayer_order"
        assert output["diagnosis"]["user_layer_found"] is True


class TestStackOnly:
    """Test --stack-only mode."""
    
    def test_stack_only_no_diagnosis(self, stages_dir):
        """Test that --stack-only skips diagnosis."""
        stage = os.path.join(stages_dir, "stage_sublayer_order.usda")
        result = run_cli(stage, "/ExampleAsset", "size", "dummy.usda", "--stack-only")
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert_matches_flattened(output, stage, "/ExampleAsset", "size")
        assert output["diagnosis"] is None
        assert len(output["opinions"]) == 2
        assert output["opinions"][0]["status"] == "winning"
        assert output["opinions"][1]["status"] == "blocked"
