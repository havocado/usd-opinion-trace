# usd-opinion-trace

A CLI and GUI tool that traces USD attribute opinion resolution and explains why edits may be blocked by LIVRPS composition rules.

<img width="402" height="266" alt="image" src="https://github.com/user-attachments/assets/dc3f3f65-ff87-4fcc-8076-17b8d12aa785" />


## Installation

The simplest way to use this tool is to install directly from Github and run the GUI:
```bash
# Install from Github
pip install git+https://github.com/havocado/usd-opinion-trace.git

# Run the GUI
usd-opinion-trace-gui
```

Otherwise, clone this repo and manually install:

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

## GUI Usage

Launch the graphical interface:

```bash
python usd_opinion_trace_gui.py
# Or after pip install:
usd-opinion-trace-gui
```

The GUI provides:
- File browser for selecting USD stage and layer files
- Input fields for prim path and attribute name
- Optional time code selection
- Stack-only mode toggle
- JSON output display with copy-to-clipboard

## CLI Usage

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
