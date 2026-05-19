"""
app.py
Main application window and UI orchestration.
CalcPro — Premium Python Calculator
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os
import math
import time
import threading

# Ensure relative imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.math_engine import safe_eval, ScientificCalc, FinancialCalc, Converter, Memory, HistoryManager
from ui.theme import theme, LAYOUT, ANIM
from ui.widgets import CalcButton, CalcDisplay, SidebarItem, HistoryPanel

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False

# ─────────────────────────────────────────────
#  SPLASH SCREEN
# ─────────────────────────────────────────────

class SplashScreen(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.overrideredirect(True)
        w, h = 360, 220
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.config(bg="#0D0D0F")
        self.attributes("-topmost", True)
        self.lift()

        # Logo area
        tk.Label(self, text="◈", bg="#0D0D0F", fg="#6366F1",
                 font=("Segoe UI", 48)).pack(pady=(30, 5))
        tk.Label(self, text="CalcPro", bg="#0D0D0F", fg="#F0F0F5",
                 font=("Segoe UI", 22, "bold")).pack()
        tk.Label(self, text="Calculadora Profissional", bg="#0D0D0F", fg="#4A4A5A",
                 font=("Segoe UI", 10)).pack(pady=(2, 20))

        # Progress bar
        self.progress_frame = tk.Frame(self, bg="#1C1C1F", height=3)
        self.progress_frame.pack(fill="x", padx=40)
        self.progress_bar = tk.Frame(self.progress_frame, bg="#6366F1", height=3, width=0)
        self.progress_bar.place(x=0, y=0)

        self._progress = 0
        self._animate_progress()

    def _animate_progress(self):
        if self._progress <= 100:
            target_w = int((280) * self._progress / 100)
            self.progress_bar.config(width=target_w)
            self._progress += 2
            self.after(20, self._animate_progress)

    def close(self):
        self.destroy()


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────

class CalcProApp:
    """
    Main application class for CalcPro.
    Manages all panels, state, and event routing.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide during splash

        # Core state
        self.expression = ""
        self.result_shown = False
        self.sci = ScientificCalc("DEG")
        self.fin = FinancialCalc()
        self.converter = Converter()
        self.memory = Memory()
        self.history = HistoryManager()
        self.compact_mode = False
        self._buttons: list[CalcButton] = []
        self._sidebar_items: list[SidebarItem] = []
        self._active_panel = "basic"

        # Splash
        splash = SplashScreen(self.root)
        self.root.after(ANIM["splash"], lambda: (splash.close(), self._build_main()))

        self.root.mainloop()

    # ──────────────────────────────────────────
    #  BUILD MAIN WINDOW
    # ──────────────────────────────────────────

    def _build_main(self):
        p = theme.palette
        self.root.title("CalcPro")
        self.root.configure(bg=p["bg_root"])
        self.root.deiconify()

        w, h = LAYOUT["window_w"], LAYOUT["window_h"]
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(700, 520)
        self.root.resizable(True, True)

        # Window decorations
        try:
            self.root.iconbitmap("")
        except Exception:
            pass

        self._build_layout()
        self._bind_keyboard()
        self._show_panel("basic")

    def _build_layout(self):
        p = theme.palette

        # ── Sidebar ──────────────────────────
        self.sidebar = tk.Frame(self.root, bg=p["bg_sidebar"],
                                 width=LAYOUT["sidebar_w"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        # Vertical separator
        tk.Frame(self.root, bg=p["border"], width=1).pack(side="left", fill="y")

        # ── Main content area ─────────────────
        self.content_area = tk.Frame(self.root, bg=p["bg_root"])
        self.content_area.pack(side="left", fill="both", expand=True)

        # Panel container
        self.panel_container = tk.Frame(self.content_area, bg=p["bg_root"])
        self.panel_container.pack(fill="both", expand=True)

        # Pre-build all panels
        self.panels = {}
        self._build_basic_panel()
        self._build_scientific_panel()
        self._build_converters_panel()
        self._build_finance_panel()
        self._build_graph_panel()
        self._build_history_panel_ui()

    def _build_sidebar(self):
        p = theme.palette
        sb = self.sidebar

        # Logo
        logo_frame = tk.Frame(sb, bg=p["bg_sidebar"])
        logo_frame.pack(fill="x", pady=(16, 4))
        tk.Label(logo_frame, text="◈", bg=p["bg_sidebar"], fg=p["accent"],
                 font=("Segoe UI", 22)).pack()
        tk.Label(logo_frame, text="CalcPro", bg=p["bg_sidebar"], fg=p["text_primary"],
                 font=("Segoe UI", 13, "bold")).pack()

        tk.Frame(sb, bg=p["border"], height=1).pack(fill="x", padx=16, pady=10)

        # Navigation items
        nav_items = [
            ("⊞", "Básica",       "basic"),
            ("∑", "Científica",   "scientific"),
            ("⇄", "Conversores",  "converters"),
            ("$", "Financeiro",   "finance"),
            ("∿", "Gráficos",     "graph"),
            ("⏱", "Histórico",    "history"),
        ]

        for icon, label, panel_id in nav_items:
            item = SidebarItem(
                sb, icon=icon, label=label,
                command=lambda p=panel_id: self._show_panel(p),
                active=(panel_id == "basic"),
                bg=p["bg_sidebar"],
                active_color=p["accent"],
                text_color=p["text_secondary"],
                active_text=p["text_primary"],
            )
            item.pack(fill="x", pady=1)
            item._panel_id = panel_id
            self._sidebar_items.append(item)

        # Bottom controls
        tk.Frame(sb, bg=p["border"], height=1).pack(fill="x", padx=16, pady=10, side="bottom")

        bottom = tk.Frame(sb, bg=p["bg_sidebar"])
        bottom.pack(side="bottom", fill="x", pady=8)

        # Theme toggle
        self.theme_btn = tk.Label(
            bottom, text="☀" if theme.is_dark() else "☾",
            bg=p["bg_sidebar"], fg=p["text_secondary"],
            font=("Segoe UI", 16), cursor="hand2",
        )
        self.theme_btn.pack(pady=4)
        self.theme_btn.bind("<Button-1>", lambda e: self._toggle_theme())

        # Compact mode toggle
        compact_lbl = tk.Label(
            bottom, text="⊡ Compacto",
            bg=p["bg_sidebar"], fg=p["text_muted"],
            font=("Segoe UI", 9), cursor="hand2",
        )
        compact_lbl.pack(pady=2)
        compact_lbl.bind("<Button-1>", lambda e: self._toggle_compact())

    # ──────────────────────────────────────────
    #  BASIC PANEL
    # ──────────────────────────────────────────

    def _build_basic_panel(self):
        p = theme.palette
        frame = tk.Frame(self.panel_container, bg=p["bg_root"])
        self.panels["basic"] = frame

        # Display
        self.display = CalcDisplay(
            frame,
            bg_color=p["display_bg"],
            text_color=p["display_text"],
            expr_color=p["display_expr"],
        )
        self.display.pack(fill="x", padx=0, pady=0)

        # Button grid
        btn_area = tk.Frame(frame, bg=p["bg_root"])
        btn_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Memory row
        mem_row = tk.Frame(btn_area, bg=p["bg_root"])
        mem_row.pack(fill="x", pady=(0, 4))
        for txt, cmd in [("MC", self._mem_clear), ("MR", self._mem_recall),
                          ("M+", self._mem_add),  ("M-", self._mem_sub)]:
            b = CalcButton(mem_row, txt, cmd,
                           bg_color=p["btn_action"], hover_color=p["bg_hover"],
                           text_color=p["text_secondary"],
                           font_spec=("Segoe UI", 10, "bold"),
                           radius=8, width=66, height=30)
            b.pack(side="left", padx=2, expand=True)
            self._buttons.append(b)

        # Main button grid layout
        grid_layout = [
            # Row 1
            [("AC",  self._clear_all,    "clear"),  ("⌫",  self._backspace,  "action"),
             ("%",   lambda: self._op("%"), "operator"),  ("÷",  lambda: self._op("÷"), "operator")],
            # Row 2
            [("7",   lambda: self._num("7"), "number"), ("8", lambda: self._num("8"), "number"),
             ("9",   lambda: self._num("9"), "number"), ("×", lambda: self._op("×"),  "operator")],
            # Row 3
            [("4",   lambda: self._num("4"), "number"), ("5", lambda: self._num("5"), "number"),
             ("6",   lambda: self._num("6"), "number"), ("−", lambda: self._op("−"),  "operator")],
            # Row 4
            [("1",   lambda: self._num("1"), "number"), ("2", lambda: self._num("2"), "number"),
             ("3",   lambda: self._num("3"), "number"), ("+", lambda: self._op("+"),  "operator")],
            # Row 5
            [("±",   self._negate,         "action"),   ("0", lambda: self._num("0"), "number"),
             (".",   lambda: self._num("."), "number"),  ("=", self._calculate,        "equals")],
        ]

        # Extra row: parentheses + powers
        extra_row = tk.Frame(btn_area, bg=p["bg_root"])
        extra_row.pack(fill="x", pady=(0, 4))
        extra_btns = [
            ("(",  lambda: self._num("("),    "action"),
            (")",  lambda: self._num(")"),    "action"),
            ("x²", lambda: self._append_fn("**2"), "operator"),
            ("√",  lambda: self._append_fn("√("),  "operator"),
        ]
        for txt, cmd, kind in extra_btns:
            clr = self._btn_colors(kind)
            b = CalcButton(extra_row, txt, cmd,
                           bg_color=clr[0], hover_color=clr[1],
                           text_color=clr[2],
                           font_spec=("Segoe UI", 13, "bold"),
                           radius=10, width=80, height=36)
            b.pack(side="left", padx=2, expand=True)
            self._buttons.append(b)

        # Main grid
        grid_frame = tk.Frame(btn_area, bg=p["bg_root"])
        grid_frame.pack(fill="both", expand=True)

        for row_data in grid_layout:
            row_frame = tk.Frame(grid_frame, bg=p["bg_root"])
            row_frame.pack(fill="x", pady=2)
            for (txt, cmd, kind) in row_data:
                clr = self._btn_colors(kind)
                font = ("Segoe UI", 20, "bold") if kind == "operator" else \
                       ("Segoe UI", 18, "normal") if kind == "number" else \
                       ("Segoe UI", 14, "bold")
                b = CalcButton(row_frame, txt, cmd,
                               bg_color=clr[0], hover_color=clr[1],
                               text_color=clr[2],
                               font_spec=font,
                               radius=12, height=LAYOUT["btn_h"])
                b.pack(side="left", padx=2, expand=True, fill="x")
                self._buttons.append(b)

    def _btn_colors(self, kind: str) -> tuple:
        p = theme.palette
        mapping = {
            "number":   (p["btn_number"],   p["btn_number_hover"],   p["text_primary"]),
            "operator": (p["btn_operator"], p["btn_operator_hover"],  p["accent"]),
            "equals":   (p["btn_equals"],   p["btn_equals_hover"],    "#FFFFFF"),
            "clear":    (p["btn_clear"],    p["btn_clear_hover"],     p["error"]),
            "action":   (p["btn_action"],   p["bg_hover"],            p["text_secondary"]),
            "sci":      (p["btn_sci"],      p["btn_sci_hover"],       p["text_accent"]),
        }
        return mapping.get(kind, mapping["action"])

    # ──────────────────────────────────────────
    #  SCIENTIFIC PANEL
    # ──────────────────────────────────────────

    def _build_scientific_panel(self):
        p = theme.palette
        frame = tk.Frame(self.panel_container, bg=p["bg_root"])
        self.panels["scientific"] = frame

        # Shared display reference
        self.sci_display = CalcDisplay(
            frame, bg_color=p["display_bg"],
            text_color=p["display_text"], expr_color=p["display_expr"],
        )
        self.sci_display.pack(fill="x")

        # Angle mode toggle
        mode_frame = tk.Frame(frame, bg=p["bg_root"])
        mode_frame.pack(fill="x", padx=10, pady=(6, 2))

        self.angle_var = tk.StringVar(value="DEG")
        for mode in ("DEG", "RAD"):
            rb = tk.Radiobutton(
                mode_frame, text=mode, variable=self.angle_var,
                value=mode, command=self._set_angle_mode,
                bg=p["bg_root"], fg=p["text_secondary"],
                selectcolor=p["accent_muted"],
                activebackground=p["bg_root"],
                font=("Segoe UI", 10, "bold"),
                relief="flat", bd=0,
            )
            rb.pack(side="left", padx=6)

        # Sci button grid
        sci_area = tk.Frame(frame, bg=p["bg_root"])
        sci_area.pack(fill="both", expand=True, padx=10, pady=6)

        sci_layout = [
            [("sin",  lambda: self._sci_fn("sin")),   ("cos",  lambda: self._sci_fn("cos")),
             ("tan",  lambda: self._sci_fn("tan")),   ("π",    lambda: self._num(str(round(math.pi, 8))))],

            [("sin⁻¹", lambda: self._sci_fn("asin")), ("cos⁻¹", lambda: self._sci_fn("acos")),
             ("tan⁻¹", lambda: self._sci_fn("atan")), ("e",    lambda: self._num(str(round(math.e, 8))))],

            [("sinh", lambda: self._sci_fn("sinh")),  ("cosh", lambda: self._sci_fn("cosh")),
             ("tanh", lambda: self._sci_fn("tanh")),  ("x!",  lambda: self._sci_fn("factorial"))],

            [("log",  lambda: self._sci_fn("log")),   ("ln",   lambda: self._sci_fn("ln")),
             ("|x|",  lambda: self._sci_fn("abs")),   ("1/x", lambda: self._sci_fn("reciprocal"))],

            [("xʸ",   lambda: self._op("**")),         ("√x",  lambda: self._sci_fn("sqrt")),
             ("exp",  lambda: self._sci_fn("exp")),   ("EE",  lambda: self._append_fn("e"))],

            [("AC",   self._clear_all),  ("⌫", self._backspace),
             ("(",    lambda: self._num("(")),  ("=",  self._calculate)],
        ]

        for row_data in sci_layout:
            row_frame = tk.Frame(sci_area, bg=p["bg_root"])
            row_frame.pack(fill="x", pady=2)
            for item in row_data:
                txt, cmd = item
                is_eq    = txt == "="
                is_clear = txt == "AC"
                is_num   = txt in ("π", "e")
                clr = self._btn_colors("equals" if is_eq else "clear" if is_clear
                                        else "number" if is_num else "sci")
                b = CalcButton(row_frame, txt, cmd,
                               bg_color=clr[0], hover_color=clr[1],
                               text_color=clr[2],
                               font_spec=("Segoe UI", 12, "bold"),
                               radius=10, height=44)
                b.pack(side="left", padx=2, expand=True, fill="x")
                self._buttons.append(b)

    # ──────────────────────────────────────────
    #  CONVERTERS PANEL
    # ──────────────────────────────────────────

    def _build_converters_panel(self):
        p = theme.palette
        frame = tk.Frame(self.panel_container, bg=p["bg_root"])
        self.panels["converters"] = frame

        tk.Label(frame, text="Conversores de Unidades", bg=p["bg_root"],
                 fg=p["text_primary"], font=("Segoe UI", 15, "bold")).pack(pady=(16, 4))

        # Notebook tabs
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TNotebook", background=p["bg_root"], borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                         background=p["bg_card"], foreground=p["text_secondary"],
                         padding=[14, 6], font=("Segoe UI", 10))
        style.map("Custom.TNotebook.Tab",
                   background=[("selected", p["accent"])],
                   foreground=[("selected", "#FFFFFF")])

        nb = ttk.Notebook(frame, style="Custom.TNotebook")
        nb.pack(fill="both", expand=True, padx=16, pady=8)

        # Temperature tab
        temp_tab = tk.Frame(nb, bg=p["bg_root"])
        nb.add(temp_tab, text="🌡 Temperatura")
        self._build_temp_converter(temp_tab)

        # Length tab
        len_tab = tk.Frame(nb, bg=p["bg_root"])
        nb.add(len_tab, text="📏 Comprimento")
        self._build_unit_converter(len_tab, Converter.LENGTH, "Comprimento")

        # Weight tab
        wt_tab = tk.Frame(nb, bg=p["bg_root"])
        nb.add(wt_tab, text="⚖ Massa")
        self._build_unit_converter(wt_tab, Converter.WEIGHT, "Massa")

        # Area tab
        area_tab = tk.Frame(nb, bg=p["bg_root"])
        nb.add(area_tab, text="▭ Área")
        self._build_unit_converter(area_tab, Converter.AREA, "Área")

        # Volume tab
        vol_tab = tk.Frame(nb, bg=p["bg_root"])
        nb.add(vol_tab, text="🧪 Volume")
        self._build_unit_converter(vol_tab, Converter.VOLUME, "Volume")

        # Speed tab
        spd_tab = tk.Frame(nb, bg=p["bg_root"])
        nb.add(spd_tab, text="🏎 Velocidade")
        self._build_unit_converter(spd_tab, Converter.SPEED, "Velocidade")

    def _converter_row(self, parent, label, value_var, options, row=0):
        p = theme.palette
        tk.Label(parent, text=label, bg=p["bg_root"], fg=p["text_secondary"],
                 font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", padx=8, pady=4)
        entry = tk.Entry(parent, textvariable=value_var, bg=p["bg_card"],
                          fg=p["text_primary"], insertbackground=p["text_primary"],
                          font=("Consolas", 13), relief="flat",
                          highlightthickness=1, highlightcolor=p["accent"],
                          highlightbackground=p["border"], width=14)
        entry.grid(row=row, column=1, padx=8, pady=4)
        combo = ttk.Combobox(parent, values=options, state="readonly",
                              font=("Segoe UI", 10), width=8)
        combo.grid(row=row, column=2, padx=8, pady=4)
        combo.current(0)
        return entry, combo

    def _build_temp_converter(self, parent):
        p = theme.palette
        parent.columnconfigure(1, weight=1)

        conversions = ["C→F", "F→C", "C→K", "K→C", "F→K", "K→F"]
        self.temp_val  = tk.StringVar()
        self.temp_conv = tk.StringVar(value=conversions[0])
        self.temp_res  = tk.StringVar(value="—")

        tk.Label(parent, text="Valor:", bg=p["bg_root"], fg=p["text_secondary"],
                 font=("Segoe UI", 11)).grid(row=0, column=0, padx=16, pady=12, sticky="w")
        tk.Entry(parent, textvariable=self.temp_val,
                  bg=p["bg_card"], fg=p["text_primary"],
                  insertbackground=p["text_primary"],
                  font=("Consolas", 14), relief="flat",
                  highlightthickness=1, highlightcolor=p["accent"],
                  highlightbackground=p["border"], width=14
                  ).grid(row=0, column=1, padx=8, pady=12)

        tk.Label(parent, text="Conversão:", bg=p["bg_root"], fg=p["text_secondary"],
                 font=("Segoe UI", 11)).grid(row=1, column=0, padx=16, pady=4, sticky="w")

        style = ttk.Style()
        style.configure("Dark.TCombobox",
                          fieldbackground=p["bg_card"], background=p["bg_card"],
                          foreground=p["text_primary"], selectbackground=p["accent"])
        combo = ttk.Combobox(parent, values=conversions,
                              textvariable=self.temp_conv,
                              style="Dark.TCombobox",
                              font=("Segoe UI", 11), state="readonly", width=10)
        combo.grid(row=1, column=1, padx=8, pady=4)

        def do_convert():
            try:
                v = float(self.temp_val.get())
                r = Converter.temperature(v, self.temp_conv.get())
                self.temp_res.set(f"{r:.4f}")
            except Exception as ex:
                self.temp_res.set(f"Erro: {ex}")

        CalcButton(parent, "Converter", do_convert,
                   bg_color=p["accent"], hover_color=p["accent_hover"],
                   text_color="#FFFFFF", font_spec=("Segoe UI", 12, "bold"),
                   radius=10, width=120, height=40,
                   ).grid(row=2, column=0, columnspan=2, pady=12, padx=16, sticky="w")

        tk.Label(parent, text="Resultado:", bg=p["bg_root"], fg=p["text_secondary"],
                 font=("Segoe UI", 11)).grid(row=3, column=0, padx=16, pady=4, sticky="w")
        tk.Label(parent, textvariable=self.temp_res,
                  bg=p["bg_root"], fg=p["accent"],
                  font=("Segoe UI", 22, "bold")).grid(row=3, column=1, padx=8, sticky="w")

    def _build_unit_converter(self, parent, table: dict, name: str):
        p = theme.palette
        units = list(table.keys())
        parent.columnconfigure(1, weight=1)

        tk.Label(parent, text=f"De:", bg=p["bg_root"], fg=p["text_secondary"],
                 font=("Segoe UI", 11)).grid(row=0, column=0, padx=16, pady=12, sticky="w")

        val_var = tk.StringVar()
        tk.Entry(parent, textvariable=val_var, bg=p["bg_card"], fg=p["text_primary"],
                  insertbackground=p["text_primary"], font=("Consolas", 14),
                  relief="flat", highlightthickness=1, highlightcolor=p["accent"],
                  highlightbackground=p["border"], width=14,
                  ).grid(row=0, column=1, padx=8, pady=12)

        from_var = tk.StringVar(value=units[0])
        to_var   = tk.StringVar(value=units[1] if len(units) > 1 else units[0])

        tk.Label(parent, text="Unidade origem:", bg=p["bg_root"], fg=p["text_secondary"],
                 font=("Segoe UI", 11)).grid(row=1, column=0, padx=16, pady=4, sticky="w")
        ttk.Combobox(parent, values=units, textvariable=from_var,
                      font=("Segoe UI", 11), state="readonly", width=10,
                      ).grid(row=1, column=1, padx=8, pady=4)

        tk.Label(parent, text="Unidade destino:", bg=p["bg_root"], fg=p["text_secondary"],
                 font=("Segoe UI", 11)).grid(row=2, column=0, padx=16, pady=4, sticky="w")
        ttk.Combobox(parent, values=units, textvariable=to_var,
                      font=("Segoe UI", 11), state="readonly", width=10,
                      ).grid(row=2, column=1, padx=8, pady=4)

        result_var = tk.StringVar(value="—")

        def do_convert():
            try:
                v = float(val_var.get())
                r = Converter.convert(v, from_var.get(), to_var.get(), table)
                result_var.set(f"{r:g} {to_var.get()}")
            except Exception as ex:
                result_var.set(f"Erro: {ex}")

        CalcButton(parent, "Converter", do_convert,
                   bg_color=p["accent"], hover_color=p["accent_hover"],
                   text_color="#FFFFFF", font_spec=("Segoe UI", 12, "bold"),
                   radius=10, width=120, height=40,
                   ).grid(row=3, column=0, columnspan=2, pady=12, padx=16, sticky="w")

        tk.Label(parent, text="Resultado:", bg=p["bg_root"], fg=p["text_secondary"],
                 font=("Segoe UI", 11)).grid(row=4, column=0, padx=16, pady=4, sticky="w")
        tk.Label(parent, textvariable=result_var,
                  bg=p["bg_root"], fg=p["accent"],
                  font=("Segoe UI", 20, "bold")).grid(row=4, column=1, padx=8, sticky="w")
