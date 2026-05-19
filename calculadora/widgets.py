"""
widgets.py
Custom reusable UI components built on tkinter.
Provides premium-looking buttons, display, and panels.
"""

import tkinter as tk
from tkinter import font as tkfont
import time


# ─────────────────────────────────────────────
#  HELPER: Interpolate hex colors for hover fx
# ─────────────────────────────────────────────

def _lerp_color(c1: str, c2: str, t: float) -> str:
    """Linear interpolation between two hex colors."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────
#  PREMIUM BUTTON
# ─────────────────────────────────────────────

class CalcButton(tk.Canvas):
    """
    Premium calculator button with smooth hover animation,
    press feedback, and customizable appearance.
    """

    def __init__(self, parent, text: str, command=None,
                 bg_color="#1C1C1F", hover_color="#2C2C31",
                 text_color="#F0F0F5", font_spec=None,
                 radius=12, width=70, height=56,
                 tag="", sound_fn=None, **kwargs):

        super().__init__(parent, width=width, height=height,
                         bg=parent.cget("bg"), highlightthickness=0,
                         bd=0, **kwargs)

        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_spec = font_spec or ("Segoe UI", 16, "normal")
        self.radius = radius
        self.w = width
        self.h = height
        self.tag = tag
        self.sound_fn = sound_fn
        self._pressed = False
        self._hover = False
        self._anim_id = None
        self._current_color = bg_color

        self._draw()
        self._bind_events()

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """Draw a rounded rectangle on canvas."""
        self.delete("all")
        points = [
            x1+r, y1, x2-r, y1,
            x2, y1, x2, y1+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r,
            x1, y1+r, x1, y1,
        ]
        self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, color=None):
        c = color or self._current_color
        self._rounded_rect(2, 2, self.w-2, self.h-2,
                            self.radius, fill=c, outline="")

        # Subtle top highlight for depth
        if not self._pressed:
            self.create_line(
                2+self.radius, 3, self.w-2-self.radius, 3,
                fill=_lerp_color(c, "#FFFFFF", 0.08), width=1
            )

        # Label
        self.create_text(
            self.w // 2, self.h // 2,
            text=self.text,
            fill=self.text_color,
            font=self.font_spec,
        )

    def _bind_events(self):
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _animate_to(self, target_color: str, steps=8, delay=12):
        """Smoothly animate background to target color."""
        if self._anim_id:
            self.after_cancel(self._anim_id)
        start_color = self._current_color
        self._anim_step(start_color, target_color, 0, steps, delay)

    def _anim_step(self, start, end, step, total, delay):
        t = step / total
        t = t * t * (3 - 2 * t)  # smoothstep easing
        color = _lerp_color(start, end, t)
        self._current_color = color
        self._draw(color)
        if step < total:
            self._anim_id = self.after(delay, self._anim_step,
                                        start, end, step+1, total, delay)

    def _on_enter(self, _):
        self._hover = True
        self._animate_to(self.hover_color, steps=6, delay=10)
        self.config(cursor="hand2")

    def _on_leave(self, _):
        self._hover = False
        self._animate_to(self.bg_color, steps=6, delay=10)
        self.config(cursor="")

    def _on_press(self, _):
        self._pressed = True
        # Scale-down effect: redraw smaller
        press_color = _lerp_color(self.hover_color, "#000000", 0.1)
        self._current_color = press_color
        self._draw(press_color)
        if self.sound_fn:
            try: self.sound_fn()
            except Exception: pass

    def _on_release(self, e):
        self._pressed = False
        self._animate_to(self.hover_color if self._hover else self.bg_color)
        if self.command:
            self.command()

    def update_theme(self, bg_color, hover_color, text_color):
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self._current_color = bg_color
        self._draw()

    def set_text(self, text):
        self.text = text
        self._draw()


# ─────────────────────────────────────────────
#  DISPLAY WIDGET
# ─────────────────────────────────────────────

class CalcDisplay(tk.Frame):
    """
    Premium multi-line calculator display.
    Shows expression (secondary) and result (primary).
    """

    def __init__(self, parent, bg_color="#0D0D0F",
                 text_color="#F0F0F5", expr_color="#6A6A8A",
                 font_result=None, font_expr=None, **kwargs):

        super().__init__(parent, bg=bg_color, **kwargs)

        self.bg_color = bg_color
        self.text_color = text_color
        self.expr_color = expr_color

        # Memory indicator
        self.mem_var = tk.StringVar(value="")
        self.mem_label = tk.Label(
            self, textvariable=self.mem_var,
            bg=bg_color, fg="#6366F1",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self.mem_label.pack(side="top", anchor="w", padx=16, pady=(8, 0))

        # Angle mode indicator
        self.mode_var = tk.StringVar(value="DEG")
        self.mode_label = tk.Label(
            self, textvariable=self.mode_var,
            bg=bg_color, fg="#5A5A7A",
            font=("Segoe UI", 9, "normal"),
            anchor="e",
        )
        self.mode_label.place(relx=1.0, y=8, anchor="ne", x=-16)

        # Expression line
        self.expr_var = tk.StringVar(value="")
        self.expr_label = tk.Label(
            self, textvariable=self.expr_var,
            bg=bg_color, fg=expr_color,
            font=font_expr or ("Segoe UI", 13, "normal"),
            anchor="e", justify="right",
        )
        self.expr_label.pack(side="top", fill="x", padx=16, pady=(4, 0))

        # Result line
        self.result_var = tk.StringVar(value="0")
        self.result_label = tk.Label(
            self, textvariable=self.result_var,
            bg=bg_color, fg=text_color,
            font=font_result or ("Segoe UI", 36, "bold"),
            anchor="e", justify="right",
        )
        self.result_label.pack(side="top", fill="x", padx=16, pady=(0, 10))

        # Bottom separator
        tk.Frame(self, bg="#1E1E24", height=1).pack(fill="x", side="bottom")

    def set_result(self, text: str):
        # Auto-shrink font for long numbers
        length = len(str(text))
        if length > 15:
            size = 20
        elif length > 10:
            size = 26
        elif length > 7:
            size = 30
        else:
            size = 36
        self.result_label.config(
            font=("Segoe UI", size, "bold"),
            text=text,
        )
        self.result_var.set(text)

    def set_expr(self, text: str): self.expr_var.set(text)
    def set_mem(self, text: str): self.mem_var.set(text)
    def set_mode(self, text: str): self.mode_var.set(text)

    def flash_error(self):
        """Brief red flash on error."""
        orig = self.result_label.cget("fg")
        self.result_label.config(fg="#EF4444")
        self.after(400, lambda: self.result_label.config(fg=orig))

    def update_colors(self, bg_color, text_color, expr_color):
        self.bg_color = bg_color
        self.config(bg=bg_color)
        self.mem_label.config(bg=bg_color)
        self.mode_label.config(bg=bg_color)
        self.expr_label.config(bg=bg_color, fg=expr_color)
        self.result_label.config(bg=bg_color, fg=text_color)


# ─────────────────────────────────────────────
#  SIDEBAR NAV BUTTON
# ─────────────────────────────────────────────

class SidebarItem(tk.Frame):
    """Sidebar navigation item with icon and label."""

    def __init__(self, parent, icon: str, label: str,
                 command=None, active=False,
                 bg="#111113", active_color="#6366F1",
                 text_color="#8A8A9A", active_text="#FFFFFF",
                 **kwargs):

        super().__init__(parent, bg=bg, cursor="hand2", **kwargs)
        self.bg = bg
        self.active_color = active_color
        self.text_color = text_color
        self.active_text = active_text
        self.command = command
        self._active = active

        self.indicator = tk.Frame(self, bg=bg, width=3)
        self.indicator.pack(side="left", fill="y")

        self.icon_lbl = tk.Label(self, text=icon, bg=bg,
                                  fg=text_color, font=("Segoe UI", 16))
        self.icon_lbl.pack(side="left", padx=(10, 6), pady=10)

        self.text_lbl = tk.Label(self, text=label, bg=bg,
                                  fg=text_color, font=("Segoe UI", 12))
        self.text_lbl.pack(side="left")

        self.set_active(active)

        for w in (self, self.icon_lbl, self.text_lbl, self.indicator):
            w.bind("<Button-1>", self._clicked)
            w.bind("<Enter>", self._hover_on)
            w.bind("<Leave>", self._hover_off)

    def _clicked(self, _):
        if self.command: self.command()

    def _hover_on(self, _):
        if not self._active:
            for w in (self, self.icon_lbl, self.text_lbl):
                w.config(bg=_lerp_color(self.bg, "#FFFFFF", 0.04))

    def _hover_off(self, _):
        if not self._active:
            for w in (self, self.icon_lbl, self.text_lbl):
                w.config(bg=self.bg)
            self.indicator.config(bg=self.bg)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.indicator.config(bg=self.active_color)
            fg = self.active_text
            bg = _lerp_color(self.bg, self.active_color, 0.12)
        else:
            self.indicator.config(bg=self.bg)
            fg = self.text_color
            bg = self.bg
        self.config(bg=bg)
        self.icon_lbl.config(bg=bg, fg=fg)
        self.text_lbl.config(bg=bg, fg=fg)

    def update_theme(self, bg, active_color, text_color, active_text):
        self.bg = bg
        self.active_color = active_color
        self.text_color = text_color
        self.active_text = active_text
        self.set_active(self._active)


# ─────────────────────────────────────────────
#  HISTORY PANEL
# ─────────────────────────────────────────────

class HistoryPanel(tk.Frame):
    """Scrollable calculation history panel."""

    def __init__(self, parent, bg="#141416", text_color="#8A8A9A",
                 accent="#6366F1", on_select=None, **kwargs):

        super().__init__(parent, bg=bg, **kwargs)
        self.bg = bg
        self.text_color = text_color
        self.accent = accent
        self.on_select = on_select

        # Header
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(hdr, text="Histórico", bg=bg,
                 fg=text_color, font=("Segoe UI", 11, "bold")).pack(side="left")

        # Canvas + scrollbar
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical",
                                       command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_configure(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, e):
        self.canvas.itemconfig(self._window, width=e.width)

    def _on_mousewheel(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def load(self, entries: list):
        for w in self.inner.winfo_children():
            w.destroy()

        if not entries:
            tk.Label(self.inner, text="Sem histórico ainda",
                     bg=self.bg, fg=self.text_color,
                     font=("Segoe UI", 11)).pack(pady=20)
            return

        for entry in reversed(entries):
            row = tk.Frame(self.inner, bg=self.bg, cursor="hand2")
            row.pack(fill="x", padx=8, pady=2)

            expr_lbl = tk.Label(row, text=entry["expression"],
                                 bg=self.bg, fg=self.text_color,
                                 font=("Consolas", 11), anchor="e", justify="right")
            expr_lbl.pack(fill="x", padx=8, pady=(4, 0))

            res_lbl = tk.Label(row, text=f"= {entry['result']}",
                                bg=self.bg, fg=self.accent,
                                font=("Segoe UI", 13, "bold"), anchor="e")
            res_lbl.pack(fill="x", padx=8, pady=(0, 2))

            ts_lbl = tk.Label(row, text=entry["timestamp"],
                               bg=self.bg, fg=_lerp_color(self.text_color, self.bg, 0.3),
                               font=("Segoe UI", 9), anchor="e")
            ts_lbl.pack(fill="x", padx=8, pady=(0, 4))

            sep = tk.Frame(row, bg=_lerp_color(self.bg, "#FFFFFF", 0.05), height=1)
            sep.pack(fill="x", padx=8)

            # Click to reuse
            val = entry["result"]
            for w in (row, expr_lbl, res_lbl):
                w.bind("<Button-1>", lambda e, v=val: self.on_select and self.on_select(v))

        self.canvas.yview_moveto(0)

    def update_theme(self, bg, text_color, accent):
        self.bg = bg
        self.text_color = text_color
        self.accent = accent
        self.canvas.config(bg=bg)
        self.inner.config(bg=bg)
        self.config(bg=bg)
