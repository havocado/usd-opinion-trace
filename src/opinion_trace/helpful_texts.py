"""
Helpful explanatory texts for the USD opinion trace tool.

These texts are reused across CLI, GUI, and other interfaces.
"""

HELPFUL_TEXTS = {
    "livrps_out_of_order": {
        "title": "Why is my layer stack not in LIVRPS order?",
        "text": (
            "LIVRPS (Local, Inherits, Variants, References, Payloads, Specializes) "
            "describes the strength ordering of composition arcs within each LayerStack, "
            "and it applies recursively. When you see what appears to be an \"out of order\" "
            "stack, such as a Reference opinion appearing stronger than a Variant opinion, "
            "it's likely because those arcs are not siblings at the same composition depth. "
            "LIVRPS ordering applies to arcs that are direct children of the same parent node "
            "in the composition graph. When one arc is nested inside another (for example, "
            "a Variant defined inside a referenced file), the parent arc's direct opinions "
            "are evaluated before recursing into child arcs.\n\n"
            "For more details, see the official USD documentation on LIVRPS Strength Ordering "
            "(https://openusd.org/release/glossary.html#liverps-strength-ordering), which states "
            "that for each arc type, USD \"recursively applies LIVERP evaluation on the targeted "
            "LayerStack.\" Also see the PcpPrimIndex documentation "
            "(https://openusd.org/release/api/class_pcp_prim_index.html) for understanding how "
            "the composition graph is structured with parent-child node relationships."
        ),
    },
}
