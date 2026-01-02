# Sample Scene: Avocado Character

A sample USD scene demonstrating all LIVRPS composition arcs for testing `usd-opinion-trace`.

## Files

```
sample_scene/
├── shot.usda                        # ★ STAGE FILE - open this
├── assets/avocado/
│   ├── avocado.usda                 # Asset with variants, inherits, specializes
│   └── avocado_geo.usda             # Heavy geometry (payload)
└── classes/
    └── _class.usda                  # Class definitions for inherits/specializes
```

## Composition Structure

```
shot.usda (STAGE)
├── SUBLAYERS: _class.usda
│   └── defines /_class_Character, /_class_OrganicMaterial
│
└── /World/Avocado (REFERENCE → avocado.usda)
    ├── INHERITS: /_class_Character
    ├── VARIANTS: expression = havoc_mode
    ├── PAYLOAD: avocado_geo.usda
    └── /Materials/Skin (SPECIALIZES: /_class_OrganicMaterial)
```

## Test Cases

### Test 1: Local Wins over Reference

```bash
python usd_opinion_trace.py sample_scene/shot.usda \
    /World/Avocado xformOp:translate avocado.usda
```

| Layer | Value | Arc |
|-------|-------|-----|
| shot.usda | `(5, 2, -3)` | **Local** ← WINS |
| avocado.usda | `(0, 0, 0)` | Reference |

**Expected diagnosis**: Local opinion in shot.usda overrides the reference.

---

### Test 2: Inherits Wins over Reference

```bash
python usd_opinion_trace.py sample_scene/shot.usda \
    /World/Avocado primvars:displayRoughness avocado.usda
```

| Layer | Value | Arc |
|-------|-------|-----|
| _class.usda | `0.25` | **Inherits** ← WINS |
| avocado.usda | `0.5` | Reference |

**Expected diagnosis**: Inherited opinion from `/_class_Character` overrides reference.

---

### Test 3: Variants Win over Payload

```bash
python usd_opinion_trace.py sample_scene/shot.usda \
    /World/Avocado/Body extent avocado_geo.usda
```

| Layer | Value | Arc |
|-------|-------|-----|
| avocado.usda (variant) | `[(-1.3, -1.6, -1.3), (1.3, 1.8, 1.3)]` | **Variants** ← WINS |
| avocado_geo.usda | `[(-1, -1.5, -1), (1, 1.5, 1)]` | Payload |

**Expected diagnosis**: Variant selection `havoc_mode` overrides payload default.

---

### Test 4: Payload Wins (view stack)

```bash
python usd_opinion_trace.py sample_scene/shot.usda \
    /World/Avocado/Body/Mesh subdivisionScheme dummy.usda --stack-only
```

| Layer | Value | Arc |
|-------|-------|-----|
| avocado_geo.usda | `"catmullClark"` | **Payload** ← WINS |

**Expected**: Only payload provides this opinion (no stronger arc defines it).

---

### Test 5: Specializes Protects Override

```bash
python usd_opinion_trace.py sample_scene/shot.usda \
    /World/Avocado/Materials/Skin inputs:roughness _class.usda
```

| Layer | Value | Arc |
|-------|-------|-----|
| avocado.usda (Skin) | `0.35` | **Specializes** ← WINS |
| _class.usda | `0.8` | Base class |

**Expected diagnosis**: Specialized opinion is protected from base class edits.

---

## LIVRPS Summary

| Arc | Typical Use | Example in Scene |
|-----|-------------|------------------|
| **L**ocal | Shot overrides | Avocado position in shot.usda |
| **I**nherits | Class-wide edits | `/_class_Character` display settings |
| **V**ariants | Asset variations | Expression: happy/hungry/havoc_mode |
| **R**eferences | Bring in assets | Avocado referenced into shot |
| **P**ayloads | Heavy geo loading | avocado_geo.usda mesh data |
| **S**pecializes | Protected materials | Skin material roughness |
