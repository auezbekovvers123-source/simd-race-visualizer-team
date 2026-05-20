"""Shared theme and operation labels — Person 1."""

THEME = {
    "bg": "#0c1018",
    "panel": "#121826",
    "panel2": "#161d2c",
    "border": "#243152",
    "text": "#e9f0ff",
    "muted": "#9fb0d0",
    "scalar": "#4cc4ff",
    "scalar_hot": "#ffcc00",
    "simd": "#5cf0a8",
    "accent": "#ffd36a",
    "track_lane": "#0f1724",
}

OP_LABEL_TO_KEY = {
    "Vector Add": "add",
    "Array Multiply": "mul",
    "Dot Product": "dot",
}
OP_KEY_TO_LABEL = {v: k for k, v in OP_LABEL_TO_KEY.items()}
