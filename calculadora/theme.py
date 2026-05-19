"""
theme.py
Design system: colors, fonts, sizes, and style configuration.
Supports dark and light themes.
"""

# ─────────────────────────────────────────────
#  COLOR PALETTES
# ─────────────────────────────────────────────

DARK_THEME = {
    # Backgrounds
    "bg_root":        "#0D0D0F",
    "bg_surface":     "#141416",
    "bg_card":        "#1C1C1F",
    "bg_elevated":    "#242428",
    "bg_hover":       "#2C2C31",
    "bg_active":      "#333339",
    "bg_sidebar":     "#111113",

    # Borders
    "border":         "#2A2A2F",
    "border_subtle":  "#1E1E22",
    "border_focus":   "#5B5BFF",

    # Text
    "text_primary":   "#F0F0F5",
    "text_secondary": "#8A8A9A",
    "text_muted":     "#4A4A5A",
    "text_accent":    "#7B7BFF",

    # Accent / Neon
    "accent":         "#6366F1",        # Indigo
    "accent_hover":   "#7C7FFF",
    "accent_glow":    "#4F52CC",
    "accent_muted":   "#1E1E3F",

    # Functional colors
    "success":        "#22C55E",
    "warning":        "#F59E0B",
    "error":          "#EF4444",
    "info":           "#3B82F6",

    # Button categories
    "btn_number":     "#1C1C1F",
    "btn_number_hover": "#2C2C31",
    "btn_operator":   "#242444",
    "btn_operator_hover": "#303060",
    "btn_action":     "#1A1A2E",
    "btn_equals":     "#6366F1",
    "btn_equals_hover": "#7C7FFF",
    "btn_clear":      "#2D1515",
    "btn_clear_hover": "#3D2020",
    "btn_sci":        "#1A2030",
    "btn_sci_hover":  "#243050",

    # Display
    "display_bg":     "#0D0D0F",
    "display_text":   "#F0F0F5",
    "display_expr":   "#6A6A8A",

    # Scrollbar
    "scrollbar":      "#2A2A35",
    "scrollbar_hover":"#3A3A45",

    # Tab
    "tab_active":     "#6366F1",
    "tab_inactive":   "#1C1C1F",
    "tab_text":       "#8A8A9A",
    "tab_text_active": "#FFFFFF",
}

LIGHT_THEME = {
    "bg_root":        "#F5F5F7",
    "bg_surface":     "#FFFFFF",
    "bg_card":        "#F0F0F3",
    "bg_elevated":    "#E8E8EC",
    "bg_hover":       "#DCDCEF",
    "bg_active":      "#D0D0E8",
    "bg_sidebar":     "#EBEBEE",

    "border":         "#D5D5DC",
    "border_subtle":  "#E5E5EA",
    "border_focus":   "#6366F1",

    "text_primary":   "#1A1A2E",
    "text_secondary": "#5A5A7A",
    "text_muted":     "#9A9AB0",
    "text_accent":    "#6366F1",

    "accent":         "#6366F1",
    "accent_hover":   "#4F52D8",
    "accent_glow":    "#C7C7FF",
    "accent_muted":   "#EDEDFF",

    "success":        "#16A34A",
    "warning":        "#D97706",
    "error":          "#DC2626",
    "info":           "#2563EB",

    "btn_number":     "#FFFFFF",
    "btn_number_hover": "#F0F0F5",
    "btn_operator":   "#EBEBff",
    "btn_operator_hover": "#DCDCFF",
    "btn_action":     "#F0F0F8",
    "btn_equals":     "#6366F1",
    "btn_equals_hover": "#4F52D8",
    "btn_clear":      "#FFE8E8",
    "btn_clear_hover": "#FFCFCF",
    "btn_sci":        "#E8EEF8",
    "btn_sci_hover":  "#D8E4F8",

    "display_bg":     "#FFFFFF",
    "display_text":   "#1A1A2E",
    "display_expr":   "#7A7A9A",

    "scrollbar":      "#D0D0DC",
    "scrollbar_hover":"#B0B0CC",

    "tab_active":     "#6366F1",
    "tab_inactive":   "#FFFFFF",
    "tab_text":       "#5A5A7A",
    "tab_text_active": "#FFFFFF",
}


# ─────────────────────────────────────────────
#  TYPOGRAPHY
# ─────────────────────────────────────────────

FONTS = {
    "display":     ("SF Pro Display", 36, "bold"),
    "display_sm":  ("SF Pro Display", 24, "bold"),
    "expr":        ("SF Pro Text",    14, "normal"),
    "label":       ("SF Pro Text",    13, "normal"),
    "label_bold":  ("SF Pro Text",    13, "bold"),
    "btn_num":     ("SF Pro Display", 18, "normal"),
    "btn_op":      ("SF Pro Display", 20, "bold"),
    "btn_func":    ("SF Pro Text",    12, "bold"),
    "mono":        ("JetBrains Mono", 13, "normal"),
    "title":       ("SF Pro Display", 15, "bold"),
    "caption":     ("SF Pro Text",    11, "normal"),
    "history":     ("JetBrains Mono", 12, "normal"),
}

# Font fallbacks for cross-platform
FONT_FAMILIES = {
    "primary":   ["SF Pro Display", "Segoe UI Variable Display", "Helvetica Neue", "Helvetica", "Arial"],
    "secondary": ["SF Pro Text", "Segoe UI Variable Text", "Helvetica Neue", "Arial"],
    "mono":      ["JetBrains Mono", "Cascadia Code", "Consolas", "Monaco", "Courier New"],
}


# ─────────────────────────────────────────────
#  SIZES & SPACING
# ─────────────────────────────────────────────

LAYOUT = {
    "window_w":       900,
    "window_h":       680,
    "sidebar_w":      200,
    "btn_h":          56,
    "btn_radius":     12,
    "display_h":      140,
    "gap":            6,
    "pad_sm":         8,
    "pad_md":         16,
    "pad_lg":         24,
    "radius_sm":      8,
    "radius_md":      12,
    "radius_lg":      18,
    "radius_xl":      24,
}

# Compact mode overrides
LAYOUT_COMPACT = {
    **LAYOUT,
    "window_w":  380,
    "window_h":  580,
    "btn_h":     48,
    "display_h": 110,
    "gap":       5,
}


# ─────────────────────────────────────────────
#  ANIMATION TIMINGS (ms)
# ─────────────────────────────────────────────

ANIM = {
    "splash":       2200,
    "fade_in":      200,
    "btn_press":    80,
    "btn_release":  120,
    "tab_switch":   150,
    "hover":        100,
}


# ─────────────────────────────────────────────
#  THEME MANAGER
# ─────────────────────────────────────────────

class ThemeManager:
    """Manages active theme and provides color lookups."""

    def __init__(self, mode: str = "dark"):
        self._mode = mode
        self._palette = DARK_THEME if mode == "dark" else LIGHT_THEME

    @property
    def mode(self): return self._mode

    @property
    def palette(self): return self._palette

    def switch(self):
        self._mode = "light" if self._mode == "dark" else "dark"
        self._palette = DARK_THEME if self._mode == "dark" else LIGHT_THEME
        return self._mode

    def color(self, key: str) -> str:
        return self._palette.get(key, "#FF00FF")  # magenta = missing key

    def is_dark(self) -> bool:
        return self._mode == "dark"


# Singleton instance
theme = ThemeManager("dark")
