# usd-opinion-trace

A CLI and GUI tool that traces USD attribute opinion resolution and explains why edits may be blocked by LIVRPS composition rules.

<img width="402" height="266" alt="image" src="https://github.com/user-attachments/assets/dc3f3f65-ff87-4fcc-8076-17b8d12aa785" />


## How to use

The simplest way to use this tool is to install directly from Github and run the GUI:
```bash
# Install from Github
pip install git+https://github.com/havocado/usd-opinion-trace.git

# Run the GUI
usd-opinion-trace-gui
```

That's it! You are good to go.

## How to use

There is a sample scene provided in this repo.

Open sample_scenes and select:
- Stage: sample_scene/shot.usda
- Prim: /World/Avocado
- Attrib: xformOpOrder
- Scene: sample_scene/assets/avocado/avocado.usda

Then press on 'Run Trace' should bring up an opinion stack with 3 arcs, and a diagnosis of `Arc Type Inherit Over Reference`.

## Install from source

To make changes to the tool, clone the repo.

Manually install:

```bash
pip install -r requirements.txt
```

Or if you want to install as package:

```bash
pip install -e .
```

## GUI Launch

Launch the graphical interface:

```bash
python usd_opinion_trace_gui.py
# Or after pip install:
usd-opinion-trace-gui
```

## CLI Usage

The core of this tool is a CLI. GUI is just a wrapper; all it does is call the CLI and display texts in a pretty way.

The CLI outputs a json, it can be checked within the GUI by selecting the json tab.

The suggestions are not output from the CLI. They live here: [reason_codes.py](https://github.com/havocado/usd-opinion-trace/blob/main/src/opinion_trace/reason_codes.py)

```bash
python usd_opinion_trace.py <stage.usd> <prim_path> <attribute> <layer> [--time <frame>] [--stack-only]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `stage.usd` | Yes | Path to USD stage file |
| `prim_path` | Yes | Prim path to query (e.g., `/World/Chair`) |
| `attribute` | Yes | Attribute name (e.g., `xformOp:translate`) |
| `layer` | Yes | User layer to diagnose (identifier or basename) |
| `--time` | No | Time code for time-sampled attributes (default: Default time) |
| `--stack-only` | No | Output opinion stack without diagnosis |

### Examples

```bash
# Full diagnosis - why is my layer's opinion not winning?
python usd_opinion_trace.py shot.usd /World/Chair xformOp:translate lighting.usd

# Query at specific frame
python usd_opinion_trace.py shot.usd /World/Chair size my_edits.usd --time 24

# Stack only - just show opinion stack without diagnosis
python usd_opinion_trace.py shot.usd /World/Chair size dummy.usd --stack-only
```

### Output

JSON object containing:

```json
{
  "query": {
    "stage": "shot.usd",
    "prim_path": "/World/Chair",
    "attribute": "size",
    "user_layer": "my_edits.usd",
    "time": null
  },
  "resolved_value": 2.0,
  "resolved_value_type": "double",
  "opinions": [
    {
      "index": 0,
      "layer": "shot.usd",
      "layer_identifier": "/path/to/shot.usd",
      "arc_type": "Local",
      "value": 2.0,
      "has_timesamples": false,
      "is_blocked": false,
      "status": "winning",
      "is_user_layer": false,
      "is_direct": true
    }
  ],
  "diagnosis": {
    "user_layer_found": true,
    "blocker_index": 0,
    "blocker_layer": "shot.usd",
    "reason": "arc_type_local_over_reference",
    "reason_detail": "Local opinions are stronger than references in LIVRPS ordering",
    "suggestions": ["Move your edit to the root layer", "Remove the blocking opinion"]
  },
  "error": null
}
```

## Running Tests

The existing tests cover one case each for reason codes. You can find them here: https://github.com/havocado/usd-opinion-trace/blob/main/tests/test_cli.py

When modifying the diagnosis, such as adding a reason code, it is important to verify it doesn't break the existing tests.

### Prerequisites

```bash
pip install pytest pytest-cov
```

### Run all tests

```bash
pytest tests/
```

### Run with coverage report

```bash
pytest tests/ --cov=usd_opinion_trace --cov-report=term-missing
```

### Run specific test class

```bash
pytest tests/test_cli.py::TestLIVRPSConflicts
```

### Run single test

```bash
pytest tests/test_cli.py::TestLIVRPSConflicts::test_local_over_reference
```

### Adding tests

Test structure example:

```python
def test_local_over_reference(self, stages_dir):
    """Test local opinion blocking reference opinion."""
    stage = os.path.join(stages_dir, "stage_local_over_reference.usda")
    output = get_diagnosis(stage, "/ExampleAsset", "size", "ref_target.usda")
    
    assert_matches_flattened(output, stage, "/ExampleAsset", "size")
    assert output["diagnosis"]["reason"] == "arc_type_local_over_reference"
    assert output["diagnosis"]["user_layer_found"] is True
    assert output["diagnosis"]["blocker_layer"] == "stage_local_over_reference.usda"
```

The first two lines calls the CLI and gets the diagnosis.

```
stage = os.path.join(stages_dir, "stage_local_over_reference.usda")
output = get_diagnosis(stage, "/ExampleAsset", "size", "ref_target.usda")
```

This is an important step - it uses the official USD API to flatten the stage to the ground truth composed scene.

```
assert_matches_flattened(output, stage, "/ExampleAsset", "size")
```

The following three lines assert the values.
